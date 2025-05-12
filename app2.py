
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import json
import requests
import calendar
import os

# Load data
with open('data/zip_to_energy_plans.json', 'r') as file:
    zip_to_plans = json.load(file)

plan_details_df = pd.read_csv('data/plan_details.csv')
gas_plan_details_df = pd.read_csv('data/gas_plan_details.csv')

# Initialize the Dash app
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

# App title
app.title = "Energy Rate Plan Optimizer"

# Create app layout
app.layout = html.Div([
    # Header
    # html.H1("Energy Rate Plan Comparison Dashboard", className='text-center mb-4'),
    html.H1(
        "Electricity Rates Comparison Dashboard",
        className='text-center',
        style={
            'background': 'linear-gradient(90deg, #2C3E50, #4CA1AF)',
            'color': 'white',
            'padding': '20px 0',
            'borderRadius': '8px',
            'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
            'fontFamily': '"Segoe UI", Roboto, "Helvetica Neue", sans-serif',
            'fontWeight': '600',
            'letterSpacing': '1px'
        }
    ),
    
    # Main content container

    dbc.Container([
        dbc.Row([
            # Left sidebar with common inputs
            dbc.Col([
                html.Div([
                    html.H4("Consumption Profile", className='mb-4 text-primary fw-bold'),
                    
                    # Location input
                    html.Label("Zip Code", className='fw-medium text-secondary mb-2'),
                    dbc.Input(
                        id="zip_input", 
                        type="text", 
                        placeholder='e.g. 94301', 
                        value="94305", 
                        className='mb-3 shadow-sm'
                    ),
                    
                    # Electricity usage input
                    html.Label("Monthly Electricity Usage", className='fw-medium text-secondary mb-2'),
                    dbc.InputGroup([
                        dbc.Input(
                            id="kwh_input", 
                            type="number", 
                            placeholder="kWh", 
                            value=400,
                            className='shadow-sm'
                        ),
                        dbc.InputGroupText("kWh", className='bg-primary text-white'),
                    ], className='mb-3'),
                    
                    # Gas usage input
                    html.Label("Monthly Gas Usage", className='fw-medium text-secondary mb-2'),
                    dbc.InputGroup([
                        dbc.Input(
                            id="therms_input", 
                            type="number", 
                            placeholder="therms", 
                            value=25,
                            className='shadow-sm'
                        ),
                        dbc.InputGroupText("therms", className='bg-primary text-white'),
                    ], className='mb-3'),
                    
                    # Baseline allowance input
                    html.Label("Gas Baseline Allowance", className='fw-medium text-secondary mb-2'),
                    dbc.InputGroup([
                        dbc.Input(
                            id="gas_allowance_input", 
                            type="number", 
                            step="0.1", 
                            placeholder="therms/day", 
                            value=1.3,
                            className='shadow-sm'
                        ),
                        dbc.InputGroupText("therms/day", className='bg-primary text-white'),
                    ], className='mb-3'),
                    
                    html.Hr(className="my-4"),
                    
                ], className='p-4 border rounded bg-light shadow-sm')
            ], width=2, className="mb-4"),
            
            # Main content area with tabs
            dbc.Col([
                html.Div([
                    # Tabs navigation
                    dbc.Tabs([
                        dbc.Tab(label="Base", tab_id="tab-base", label_style={"font-weight": "bold"}),
                        dbc.Tab(label="Electrification Simulation", tab_id="tab-electrification", label_style={"font-weight": "bold"}),
                        dbc.Tab(label="Solar Simulation", tab_id="tab-solar", label_style={"font-weight": "bold"}),
                    ], id="tabs", active_tab="tab-base", className="nav-fill"),
                    # Tab content container
                    html.Div(id="tab-content", className="p-4 border border-top-0 rounded-bottom")
                ], className="shadow-sm")
            ], width=10)
        ])
    ], fluid=True, className="py-4"),
])

# Callback to handle tab selection
@app.callback(
    dash.Output("tab-content", "children"),
    dash.Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    """Renders the content for the selected tab."""
    
    if active_tab == "tab-base":
        return html.Div([
            html.H3("Rate Comparison Tab"),
            html.P("Electricity Costs and Emissions Based on your Location"),

            # Row with Bar Chart and Pie Chart
            html.Div([
                # Bar Chart (Left)
                html.Div([
                    dcc.Graph(id='plan_comparison', style={'height': '500px'})
                ], style={
                    'width': '60%',
                    'padding': '3px',
                    'boxSizing': 'border-box'
                }),

                # Pie Chart + Dropdown (Right)
                html.Div([
                    html.Div(
                        dcc.Graph(id='power_mix_pie', style={'height': '400px'}),
                        style={'marginBottom': '20px'}
                    ),
                    html.Label("Plan for Pie Chart:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
                    dcc.Dropdown(id='plan_selector', placeholder='Select a plan',
                                style={'width': '100%', 'fontSize': '13px'})
                ], style={
                    'width': '35%',
                    'padding': '3px',
                    'boxSizing': 'border-box'
                }),
            ], style={'display': 'flex', 'flexWrap': 'wrap'}),
        ])

    
    elif active_tab == "tab-electrification":
        return html.Div([
            html.H3("Electrification Simulation Tab"),
            html.P("Electricity Costs and Emissions after Electrification"),

            # Collapsible advanced settings
            html.Div([
                dbc.Button(
                    "Advanced Configuration",
                    id="electrification-config-button",
                    color="secondary",
                    className="mb-3",
                    outline=True,
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody([
                        dbc.Row([
                            # First input
                            dbc.Col([
                                html.Label("COP:", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='cop_input', type='number', value=4, step=0.1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'})
                            ], width=1, className="px-1"),
                            
                            # Second input
                            dbc.Col([
                                html.Label("Furnace Eff (%):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='furnace_eff_input', type='number', value=80, step=1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'})
                            ], width=2, className="px-1"),
                            
                            # Third input
                            dbc.Col([
                                html.Label("Water Heater Eff (%):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='heater_eff_input', type='number', value=80, step=1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'})
                            ], width=2, className="px-1"),

                            # Slider to control Furnace vs Water Heater ratio
                            dbc.Col([
                                html.Label("Furnace vs Water Heater Gas Ratio (%)", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Slider(
                                    id='furnace_ratio_slider',
                                    min=0,
                                    max=100,
                                    step=1,
                                    value=60,
                                    marks={0: '0% Furnace', 50: '50 %', 100: '100% Furnace'},
                                    tooltip={"placement": "bottom", "always_visible": True}
                                ),
                                html.Div(id='furnace_water_ratio_display', style={'fontSize': '10px', 'marginTop': '5px'})
                            ], width=4, className="px-1"),
                            
                            # Sixth input
                            dbc.Col([
                                html.Label("Electrify (%):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='electrification_pct_input', type='number', value=100, step=1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'})
                            ], width=2, className="px-1"),
                            
                            # # Seventh input
                            # dbc.Col([
                            #     html.Label("Solar (kW):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                            #     dcc.Input(id='solar_size_input', type='number', value=4, step=0.5,
                            #             style={'width': '100%', 'height': '28px', 'padding': '2px'})
                            # ], width=1, className="px-1"),
                        ], className="mb-3 g-0")
                    ])),
                    id="electrification-config-collapse",
                    is_open=False,
                ),
            ], className="mb-4"),

            # Row with Bar Chart and Pie Chart
            html.Div([
                # Bar Chart (Left)
                html.Div([
                    dcc.Graph(id='plan_comparison_electrification', style={'height': '500px'})
                ], style={
                    'width': '60%',
                    'padding': '3px',
                    'boxSizing': 'border-box'
                }),

                # Pie Chart + Dropdown (Right)
                html.Div([
                    html.Div(
                        dcc.Graph(id='power_mix_pie', style={'height': '400px'}),
                        style={'marginBottom': '20px'}
                    ),
                    html.Label("Plan for Pie Chart:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
                    dcc.Dropdown(id='plan_selector', placeholder='Select a plan',
                                style={'width': '100%', 'fontSize': '13px'})
                ], style={
                    'width': '35%',
                    'padding': '3px',
                    'boxSizing': 'border-box'
                }),
            ], style={'display': 'flex', 'flexWrap': 'wrap'}),
        ])
    
    elif active_tab == "tab-solar":
        return html.Div([
            html.H3("Solar Simulation Tab"),
            # Collapsible advanced settings
            html.Div([
                dbc.Button(
                    "Advanced Configuration",
                    id="solar-config-button",
                    color="secondary",
                    className="mb-3",
                    outline=True,
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody([
                        dbc.Row([
                            # Solar Coverage
                            dbc.Col([
                                html.Label("Solar Coverage (%):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='solar_coverage_input', type='number', value=90, step=1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'}),
                                dbc.Tooltip("Target % of your electricity usage covered by solar", target="solar_coverage_input")
                            ], width=2, className="px-1"),

                            # Roof Space (sq ft)
                            dbc.Col([
                                html.Label("Available Roof Space (sq ft):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='roof_sqft_input', type='number', value=400, step=10,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'})
                            ], width=2, className="px-1"),

                            # Tilt (degrees)
                            dbc.Col([
                                html.Label("Tilt (°):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='tilt_input', type='number', value=20, step=1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'}),
                                dbc.Tooltip("Tilt angle of your panels in degrees", target="tilt_input")
                            ], width=1, className="px-1"),

                            # Azimuth (degrees)
                            dbc.Col([
                                html.Label("Azimuth (°):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='azimuth_input', type='number', value=180, step=1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'}),
                                dbc.Tooltip("Direction your panels face (180 = South)", target="azimuth_input")
                            ], width=1, className="px-1"),

                            # Array Type
                            dbc.Col([
                                html.Label("Array Type:", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Dropdown(
                                    id='array_type_input',
                                    options=[
                                        {'label': 'Fixed Roof Mount', 'value': 1},
                                        {'label': 'Fixed Open Rack', 'value': 0},
                                        {'label': '1-Axis Tracking', 'value': 2},
                                        {'label': '1-Axis Backtracking', 'value': 3},
                                        {'label': '2-Axis Tracking', 'value': 4}
                                    ],
                                    value=1,
                                    clearable=False,
                                    style={'fontSize': '12px'}
                                ),
                                dbc.Tooltip("Mounting style (e.g. roof or tracking system)", target="array_type_input")
                            ], width=2, className="px-1"),

                            # Module Type
                            dbc.Col([
                                html.Label("Module Type:", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Dropdown(
                                    id='module_type_input',
                                    options=[
                                        {'label': 'Standard', 'value': 0},
                                        {'label': 'Premium', 'value': 1},
                                        {'label': 'Thin Film', 'value': 2}
                                    ],
                                    value=1,
                                    clearable=False,
                                    style={'fontSize': '12px'}
                                )
                            ], width=2, className="px-1"),

                            # System Losses (%)
                            dbc.Col([
                                html.Label("System Losses (%):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='losses_input', type='number', value=14, step=1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'}),
                                dbc.Tooltip("System losses from shading, wiring, etc. (as %)", target="losses_input")
                            ], width=2, className="px-1"),

                        ], className="mb-3 g-0")
                    ])),
                    id="solar-config-collapse",
                    is_open=False,
                ),

            ], className="mb-4"),
            html.Div(id="solar-simulation-content", className="mt-4"),
            html.H5("Savings over the next 20 years (assuming 2% annual increase in electricity rates)"),
            dcc.Dropdown(id='plan_selector_solar', placeholder='Select a plan',
                                style={'width': '50%', 'fontSize': '13px'}),
            html.Div(id="solar-simulation-content-2", className="mt-4"),
            # dcc.Graph(id="fig_savings_projection", style={'width': '100%', 'height': '400px'}),
        ])
    
    # Default case
    return html.P("Please select a tab")

# Add a callback for the collapsible advanced settings section
@app.callback(
    dash.Output("electrification-config-collapse", "is_open"),
    [dash.Input("electrification-config-button", "n_clicks")],
    [dash.State("electrification-config-collapse", "is_open")],
)
def toggle_electrification_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    [Output('plan_selector', 'options'),
     Output('plan_selector', 'value')],
    Input('zip_input', 'value')
)
def update_dropdown(zip_code):
    if not zip_code:
        return [], None

    zip_code = zip_code.strip()

    if zip_code not in zip_to_plans:
        return [], None

    available_plans = zip_to_plans[zip_code]
    plans = plan_details_df[plan_details_df['plan'].isin(available_plans)]

    options = [{'label': plan, 'value': plan} for plan in plans['plan']]
    default_value = plans['plan'].iloc[0]

    return options, default_value


@app.callback(
    Output('plan_comparison', 'figure'),
    Input('zip_input', 'value'),
    Input('kwh_input', 'value'),
    Input('therms_input', 'value'),
    Input('gas_allowance_input', 'value'),
    Input("tabs", "active_tab")
)
def update_bar(zip_code, kwh_usage, therms_usage, gas_allowance, active_tab):
    """Update the bar chart based on user inputs and selected tab."""
    if not zip_code:
        return go.Figure()

    zip_code = zip_code.strip()

    if zip_code not in zip_to_plans:
        return go.Figure()

    available_plans = zip_to_plans[zip_code]
    plans = plan_details_df[plan_details_df['plan'].isin(available_plans)]

    gas_emissions_factor = 5.3  # kg CO₂ per therm

    if plans.empty:
        return go.Figure()

    elif active_tab == "tab-base":

        fig = go.Figure()

        gas_base_price = gas_plan_details_df[gas_plan_details_df['plan'] == 'PG&E Baseline']['price_per_therm'].values[0]
        gas_excess_price = gas_plan_details_df[gas_plan_details_df['plan'] == 'PG&E Excess']['price_per_therm'].values[0]

        electricity_costs = plans['price_per_kwh'] * kwh_usage
        gas_base = gas_base_price * min(therms_usage, gas_allowance * 30)
        gas_excess = gas_excess_price * max(0, therms_usage - gas_allowance * 30)
        gas_total = gas_base + gas_excess

        # Match gas cost to length of plans (assume same for all)
        gas_costs = [gas_total] * len(plans)

        elec_color_elec = '#1f77b4'      # Bold blue
        gas_color_elec = '#ff7f0e'       # Bold orange
        emission_color_elec = '#d62728'  # Strong red
        emission_color_gas = '#f2c6a0'   # Soft tan

        # First: Electricity (bottom layer of stack)
        fig.add_trace(go.Bar(
            x=plans['plan'],
            y=electricity_costs,
            name='Electricity Cost',
            marker_color=elec_color_elec,
            width=0.35,  # Slightly narrower to accommodate emissions bar
            offsetgroup='costs',
            offset=-0.2  # Shift left to make room for emissions
        ))

        # Second: Gas (stacked on top of electricity)
        fig.add_trace(go.Bar(
            x=plans['plan'],
            y=gas_costs,
            name='Gas Cost',
            marker_color=gas_color_elec,
            width=0.35,
            offsetgroup='costs',
            offset=-0.2  # Align with electricity
        ))

        # Calculate separate emissions
        electric_emissions = plans['emissions_g_per_kwh'] * kwh_usage / 1000
        gas_emissions = gas_emissions_factor * therms_usage

        # Add stacked emissions: Electricity
        fig.add_trace(go.Bar(
            x=plans['plan'],
            y=electric_emissions,
            name='Electricity Emissions',
            marker_color=emission_color_elec,
            width=0.25,
            offsetgroup='emissions',
            offset=0.15,
            opacity=0.85,
            yaxis='y2'
        ))

        # Add stacked emissions: Gas
        fig.add_trace(go.Bar(
            x=plans['plan'],
            y=[gas_emissions] * len(plans),
            name='Gas Emissions',
            marker_color=emission_color_gas,
            width=0.25,
            offsetgroup='emissions',
            offset=0.15,
            opacity=0.85,
            yaxis='y2'
        ))

        # Update layout with improved readability
        fig.update_layout(
            title={
                'text': f"Energy Rate Plans for ZIP {zip_code}",
                'font': {'size': 22, 'family': 'Arial, sans-serif'}
            },
            barmode='stack',  # Stack electricity and gas bars
            bargap=0.4,  # Increased gap between plan groups for clarity
            bargroupgap=0.1,  # Space between bars in a group
            yaxis=dict(
                title={'text': 'Monthly Cost ($)', 'font': {'size': 16}},
                side='left',
                gridcolor='lightgray',
                tickformat='$,.0f'  # Format as currency
            ),
            yaxis2=dict(
                title={'text': 'Monthly Emissions (kg CO₂)', 'font': {'size': 16}},
                overlaying='y',
                side='right',
                gridcolor='lightgray',
                range=[0, max(electric_emissions + gas_emissions) * 1.2]  # Dynamic range for emissions
            ),
            legend=dict(
                x=-0.2,              # Shift legend to the left of the chart
                y=0.5,               # Vertically centered
                xanchor="right",     # Anchor legend box by its right edge
                yanchor="middle",
                orientation='v',     # Vertical legend
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='lightgray',
                borderwidth=1,
                font=dict(size=10)
            ),
            margin=dict(l=80, r=80, t=120, b=80),
            plot_bgcolor='white',
            font=dict(family='Arial, sans-serif')
        )

        # Add hover template for better information display
        for i in range(len(fig.data)):
            if i < 2:  # Cost bars
                fig.data[i].hovertemplate = '%{y:$,.2f}<extra>%{fullData.name}</extra>'
            else:  # Emissions bar
                fig.data[i].hovertemplate = '%{y:.1f} kg CO₂<extra>%{fullData.name}</extra>'

        # Add x-axis grid lines
        fig.update_xaxes(
            tickfont=dict(size=14),
            showgrid=True,
            gridcolor='lightgray'
        )

        return fig
    
    elif active_tab == "tab-electrification":

        fig = go.Figure()

        return fig

@app.callback(
    Output("plan_comparison_electrification", "figure"),
    Input("tabs", "active_tab"),
    Input('zip_input', 'value'),
    Input('kwh_input', 'value'),
    Input('therms_input', 'value'),
    Input('gas_allowance_input', 'value'),
    Input('cop_input', 'value'),
    Input('furnace_eff_input', 'value'),
    Input('heater_eff_input', 'value'),
    Input('furnace_ratio_slider', 'value'),
    # Input('furnace_ratio_input', 'value'),
    # Input('heater_ratio_input', 'value'),
    Input('electrification_pct_input', 'value'),
    # Input('solar_size_input', 'value')
)
def update_bar_electrification(active_tab, zip_code, kwh_usage, therms_usage, gas_allowance,
                             cop, furnace_eff, heater_eff, furnace_ratio, electrification_pct):
    if active_tab != "tab-electrification":
        raise dash.exceptions.PreventUpdate

    if not zip_code:
        return go.Figure()

    zip_code = zip_code.strip()

    if zip_code not in zip_to_plans:
        return go.Figure()

    available_plans = zip_to_plans[zip_code]
    plans = plan_details_df[plan_details_df['plan'].isin(available_plans)]

    gas_emissions_factor = 5.3  # kg CO₂ per therm

    if plans.empty:
        return go.Figure()
    
    if any(v is None for v in [cop, furnace_eff, heater_eff, furnace_ratio, electrification_pct]):
        raise dash.exceptions.PreventUpdate
    
    # --- Convert to decimals ---
    furnace_ratio /= 100
    heater_ratio = 1 - furnace_ratio
    electrification_pct /= 100
    furnace_eff /= 100
    heater_eff /= 100

    # --- Calculate additional electricity usage and reduced gas ---
    additional_kwh = therms_usage * electrification_pct * (
        furnace_ratio * furnace_eff * 29.3 / cop +
        heater_ratio * heater_eff * 29.3 / cop
    )

    reduced_gas = therms_usage * (1 - electrification_pct)
    adjusted_kwh = kwh_usage + additional_kwh

    fig = go.Figure()

    # --- Load prices ---
    gas_base_price = gas_plan_details_df[gas_plan_details_df['plan'] == 'PG&E Baseline']['price_per_therm'].values[0]
    gas_excess_price = gas_plan_details_df[gas_plan_details_df['plan'] == 'PG&E Excess']['price_per_therm'].values[0]

    x_vals = []

    elec_costs = []
    gas_costs = []

    elec_colors = []
    gas_colors = []
    elec_opacities = []
    gas_opacities = []

    electric_emissions = []
    gas_emissions = []
    emission_colors = []
    emission_opacities = []

    for i, plan in enumerate(plans['plan']):
        price_per_kwh = plans.loc[plans['plan'] == plan, 'price_per_kwh'].values[0]
        emissions_factor = plans.loc[plans['plan'] == plan, 'emissions_g_per_kwh'].values[0]

        # Colors
        elec_color_original = 'lightsteelblue'
        gas_color_original = '#fdd9a0'
        elec_color_elec = '#1f77b4'      # Bold blue
        gas_color_elec = '#ff7f0e'       # Bold orange
        emission_color_elec = '#d62728'  # Strong red
        emission_color_gas = '#f2c6a0'   # Soft tan

        # --- Original ---
        gas_base_orig = gas_base_price * min(therms_usage, gas_allowance * 30)
        gas_excess_orig = gas_excess_price * max(0, therms_usage - gas_allowance * 30)
        gas_total_orig = gas_base_orig + gas_excess_orig
        elec_cost_orig = price_per_kwh * kwh_usage
        emissions_kg_orig = emissions_factor * kwh_usage / 1000
        gas_em_orig = gas_emissions_factor * therms_usage

        x_vals.append(plan + " (Original)")
        elec_costs.append(elec_cost_orig)
        gas_costs.append(gas_total_orig)
        elec_colors.append(elec_color_original)
        gas_colors.append(gas_color_original)
        elec_opacities.append(0.5)
        gas_opacities.append(0.5)
        electric_emissions.append(emissions_kg_orig)
        gas_emissions.append(gas_em_orig)
        emission_colors.append(emission_color_elec)
        emission_opacities.append(0.5)

        # --- Electrified ---
        gas_base_elec = gas_base_price * min(reduced_gas, gas_allowance * 30)
        gas_excess_elec = gas_excess_price * max(0, reduced_gas - gas_allowance * 30)
        gas_total_elec = gas_base_elec + gas_excess_elec
        elec_cost_elec = price_per_kwh * adjusted_kwh
        emissions_kg_elec = emissions_factor * adjusted_kwh / 1000
        gas_em_elec = gas_emissions_factor * reduced_gas

        x_vals.append(plan + " (Electrified)")
        elec_costs.append(elec_cost_elec)
        gas_costs.append(gas_total_elec)
        elec_colors.append(elec_color_elec)
        gas_colors.append(gas_color_elec)
        elec_opacities.append(1.0)
        gas_opacities.append(1.0)
        electric_emissions.append(emissions_kg_elec)
        gas_emissions.append(gas_em_elec)
        emission_colors.append(emission_color_elec)
        emission_opacities.append(1.0)


    # Electricity Cost Bars
    fig.add_trace(go.Bar(
        x=x_vals,
        y=elec_costs,
        name='Electricity Cost',
        marker=dict(color=elec_colors),
        opacity=None,  # use per-bar opacity
        width=0.35,
        offsetgroup='costs',
        offset=-0.2,
        customdata=elec_opacities,
        marker_opacity=elec_opacities
    ))

    # Gas Cost Bars
    fig.add_trace(go.Bar(
        x=x_vals,
        y=gas_costs,
        name='Gas Cost',
        marker=dict(color=gas_colors),
        opacity=None,
        width=0.35,
        offsetgroup='costs',
        offset=-0.2,
        customdata=gas_opacities,
        marker_opacity=gas_opacities
    ))

    # Electricity Emissions Bar
    fig.add_trace(go.Bar(
        x=x_vals,
        y=electric_emissions,
        name='Electricity Emissions',
        marker=dict(color=emission_color_elec),
        opacity=None,
        marker_opacity=emission_opacities,
        width=0.25,
        offsetgroup='emissions',
        offset=0.15,
        yaxis='y2'
    ))

    # Gas Emissions Bar
    fig.add_trace(go.Bar(
        x=x_vals,
        y=gas_emissions,
        name='Gas Emissions',
        marker=dict(color=emission_color_gas),
        opacity=None,
        marker_opacity=emission_opacities,
        width=0.25,
        offsetgroup='emissions',
        offset=0.15,
        yaxis='y2'
    ))

    # # --- Layout ---
    fig.update_layout(
        title={
            'text': f"Electrification Simulation for ZIP {zip_code}",
            'font': {'size': 18, 'family': 'Arial, sans-serif'}
        },
        barmode='stack',
        bargap=0.4,
        bargroupgap=0.1,
        yaxis=dict(
            title={'text': 'Monthly Cost ($)', 'font': {'size': 16}},
            side='left',
            gridcolor='lightgray',
            tickformat='$,.0f'
        ),
        yaxis2=dict(
            title={'text': 'Monthly Emissions (kg CO₂)', 'font': {'size': 16}},
            overlaying='y',
            side='right',
            gridcolor='lightgray',
            range=[0, max(electric_emissions + gas_emissions) * 1.2]  # Dynamic range for emissions
        ),
        legend=dict(
            x=-0.2,              # Shift legend to the left of the chart
            y=0.5,               # Vertically centered
            xanchor="right",     # Anchor legend box by its right edge
            yanchor="middle",
            orientation='v',     # Vertical legend
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='lightgray',
            borderwidth=1,
            font=dict(size=10)
        ),
        margin=dict(l=80, r=80, t=120, b=80),
        plot_bgcolor='white',
        font=dict(family='Arial, sans-serif')
    )

    # --- Hover Templates ---
    for trace in fig.data:
        if 'Emissions' in trace.name:
            trace.hovertemplate = '%{y:.1f} kg CO₂<extra>%{fullData.name}</extra>'
        else:
            trace.hovertemplate = '%{y:$,.2f}<extra>%{fullData.name}</extra>'

    fig.update_xaxes(
        tickfont=dict(size=14),
        showgrid=True,
        gridcolor='lightgray'
    )

    return fig

# Callback: Update pie chart based on selected plan
@app.callback(
    Output('power_mix_pie', 'figure'),
    Input('plan_selector', 'value')
)
def update_pie_chart(selected_plan):
    if not selected_plan:
        return go.Figure()

    # Ordered sources with cleaner labels
    power_sources = [
        "Coal", "Large Hydroelectric", "Natural Gas", "Nuclear", "Non-Renewable Other", "Unspecified",
        "Biomass & Biowaste", "Geothermal", "Eligible Hydroelectric", "Solar", "Wind", "Renewable Other"
    ]
    
    # Original column names in dataframe
    df_columns = [
        "Coal", "Large Hydroelectric", "Natural Gas", "Nuclear", "Non-Renewable_Others", "Unspecified Power",
        "Biomass & Biowaste", "Geothermal", "Eligible Hydrelectric", "Solar", "Wind", "Renewable_Others"
    ]

    # Color scheme: red-orange tones for non-renewables, green-blue for renewables
    colors = [
        # Non-Renewables (darker tones)
        "#4d0f00",  # Coal – dark reddish-brown
        "#6b200c",  # Large Hydro (controversial) – dark clay
        "#8b2c02",  # Natural Gas – rich dark orange
        "#a63603",  # Nuclear – burnt orange
        "#b15928",  # Non-Renewable Others – earthy brown
        "#666666",  # Unspecified – dark neutral gray

        # Renewables (clean, vibrant)
        "#006d2c",  # Biomass – forest green
        "#31a354",  # Geothermal – bright leaf green
        "#74c476",  # Hydroelectric – mint green
        "#fed976",  # Solar – soft yellow
        "#6baed6",  # Wind – light sky blue
        "#2171b5"   # Renewable Others – deeper blue
    ]

    row = plan_details_df[plan_details_df['plan'] == selected_plan].iloc[0]
    values = row[df_columns].astype(float).values
    
    # Group small slices into "Other" category for cleaner visualization
    threshold = 0.03  # 3% threshold
    combined_labels = []
    combined_values = []
    combined_colors = []
    is_renewable = []  # Track which slices are renewable
    
    non_renewable_small = 0
    renewable_small = 0
    
    for i, (source, value, color) in enumerate(zip(power_sources, values, colors)):
        if value < threshold:
            if i < 6:  # Non-renewable sources
                non_renewable_small += value
            else:  # Renewable sources
                renewable_small += value
        else:
            combined_labels.append(source)
            combined_values.append(value)
            combined_colors.append(color)
            is_renewable.append(i >= 6)  # True if index >= 6 (renewable)
    
    # Add combined categories if they exist
    if non_renewable_small > 0:
        combined_labels.append("Other Non-Renewable")
        combined_values.append(non_renewable_small)
        combined_colors.append("#969696")  # Gray
        is_renewable.append(False)
        
    if renewable_small > 0:
        combined_labels.append("Other Renewable")
        combined_values.append(renewable_small)
        combined_colors.append("#b3de69")  # Light green
        is_renewable.append(True)
    
    # Calculate renewable vs non-renewable percentage
    renewable_pct = sum(values[6:])
    non_renewable_pct = sum(values[:6])
    total = renewable_pct + non_renewable_pct
    
    if total > 0:
        renewable_pct = round((renewable_pct / total) * 100)
        non_renewable_pct = round((non_renewable_pct / total) * 100)
    
    # Create pull array - pull out all renewable sources
    # pull = [0.1 if is_renewable[i] else 0 for i in range(len(combined_labels))]
    
    pie_fig = go.Figure(data=[
        go.Pie(
            labels=combined_labels,
            values=combined_values,
            hole=0.4,
            marker=dict(colors=combined_colors),
            name=selected_plan,
            sort=False,
            direction='clockwise',
            rotation=0,  # Start at top
            textinfo='percent',  # Show only percentages on the chart
            textposition='inside',
            #pull=pull,  # Pull out renewable sources
            textfont=dict(size=14, color='white'),
            insidetextorientation='radial',
            domain=dict(x=[0, 0.7])  # Fix chart width to 70% of figure
        )
    ])

    pie_fig.update_layout(
        title={
            'text': f"Power Mix for {selected_plan}<br><span style='font-size:18px;color:#2ca25f'>{renewable_pct}% Renewable</span> | <span style='font-size:18px;color:#d73027'>{non_renewable_pct}% Non-Renewable</span>",
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=22),
            'y': 0.95
        },
        margin=dict(l=20, r=20, t=20, b=20),  # Increased bottom margin for legend
        height=500,  # Increased height to accommodate bottom legend
        legend=dict(
            orientation='v',
            x=0.85,       # Start legend at 75% of the width
            y=0.5,
            xanchor='left',
            yanchor='middle',
            font=dict(size=12),
            bordercolor='lightgrey',
            borderwidth=1,
            bgcolor='rgba(255, 255, 255, 0.9)',
            traceorder='normal'
        ),
        showlegend=True,
        paper_bgcolor='white'
    )

    return pie_fig

##########################
## Solar Simulation Tab ##
##########################

from geopy.geocoders import Nominatim

def zip_to_latlon(zip_code):
    geolocator = Nominatim(user_agent="solar_app")
    try:
        location = geolocator.geocode({"postalcode": zip_code}, timeout=5)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None


def fetch_solar_potential(lat, lon, system_capacity_kw=4.0, azimuth=180, tilt=20,
                          array_type=1, module_type=1, losses=14):
    """Fetches estimated solar output from NREL PVWatts API with custom params."""
    url = "https://developer.nrel.gov/api/pvwatts/v6.json"
    params = {
        "api_key": "897BGzhguuFnqgrEN2wTzPijQrA2n9xUpwytM6H8",  # Use your own API key
        "lat": lat,
        "lon": lon,
        "system_capacity": system_capacity_kw,
        "azimuth": azimuth,
        "tilt": tilt,
        "array_type": array_type,
        "module_type": module_type,
        "losses": losses,
        "dataset": "nsrdb",
        "timeframe": "monthly"
    }

    response = requests.get(url, params=params)
    print("Request URL:", response.url)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None
    
@app.callback(
    [Output('plan_selector_solar', 'options'),
     Output('plan_selector_solar', 'value')],
    Input('zip_input', 'value')
)
def update_dropdown(zip_code):
    if not zip_code:
        return [], None

    zip_code = zip_code.strip()

    if zip_code not in zip_to_plans:
        return [], None

    available_plans = zip_to_plans[zip_code]
    plans = plan_details_df[plan_details_df['plan'].isin(available_plans)]

    options = [{'label': plan, 'value': plan} for plan in plans['plan']]
    default_value = plans['plan'].iloc[0]

    return options, default_value
    
# Add a callback for the collapsible advanced settings section
@app.callback(
    dash.Output("solar-config-collapse", "is_open"),
    [dash.Input("solar-config-button", "n_clicks")],
    [dash.State("solar-config-collapse", "is_open")],
)
def toggle_electrification_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("solar-simulation-content", "children"),
    Output("solar-simulation-content-2", "children"),
    Input("tabs", "active_tab"),
    Input("zip_input", "value"),
    Input("kwh_input", "value"),
    Input("solar_coverage_input", "value"),
    Input("roof_sqft_input", "value"),
    Input("tilt_input", "value"),
    Input("azimuth_input", "value"),
    Input("array_type_input", "value"),
    Input("module_type_input", "value"),
    Input("losses_input", "value"), 
    Input("plan_selector_solar", "value")
)
def update_solar_tab(active_tab, zip_code, monthly_kwh_usage, solar_coverage_ratio_pct,
                     roof_sqft, tilt, azimuth, array_type, module_type, losses, selected_plan):
    if active_tab != "tab-solar" or not zip_code:
        raise dash.exceptions.PreventUpdate
    
    zip_code = str(zip_code).strip()
    lat, lon = zip_to_latlon(zip_code)
    if lat is None:
        return html.P("Could not geocode ZIP code."), go.Figure()

    # Estimate system size (1 kW ~ 100 sqft)
    system_capacity_kw = roof_sqft / 100.0 if roof_sqft else 4.0

    # Fetch solar output estimate
    data = fetch_solar_potential(lat, lon, system_capacity_kw, azimuth, tilt, array_type, module_type, losses)
    if not data or "outputs" not in data:
        return html.P("Failed to retrieve solar data."), go.Figure()

    monthly_kwh = data["outputs"]["ac_monthly"]
    annual_kwh = data["outputs"]["ac_annual"]

    # Convert % to ratio
    coverage_ratio = (solar_coverage_ratio_pct or 70) / 100.0

    # Compute achievable average monthly output
    avg_monthly_output = sum(monthly_kwh) / 12

    # Requested offset in kWh
    requested_offset = (monthly_kwh_usage or 0) * coverage_ratio

    # Final offset is the lesser of the two
    monthly_solar_offset = min(requested_offset, avg_monthly_output)

    # Generate warning message if user request exceeds capacity
    warning_msg = None
    if requested_offset > avg_monthly_output:
        actual_coverage = (avg_monthly_output / (monthly_kwh_usage or 1)) * 100
        warning_msg = html.Div([
            html.P(f"⚠️ Your roof space can only support about {int(actual_coverage)}% of your monthly usage.",
                style={'color': 'orange', 'fontWeight': 'bold'})
        ])
    else:
        actual_coverage = coverage_ratio * 100


    # --- Get available plans at ZIP ---
    if zip_code not in zip_to_plans:
        return html.P("No electricity plans available for this ZIP code."), go.Figure()

    available_plans = zip_to_plans[zip_code]
    plans = plan_details_df[plan_details_df['plan'].isin(available_plans)]

    # --- Cost & Emissions Savings per Plan ---
    cost_savings = []
    emissions_savings = []
    plan_labels = []

    for _, row in plans.iterrows():
        price_per_kwh = row['price_per_kwh']
        emissions_factor = row['emissions_g_per_kwh']  # g CO₂ per kWh

        monthly_cost_saving = monthly_solar_offset * price_per_kwh
        monthly_emissions_saving = (monthly_solar_offset * emissions_factor) / 1000  # kg CO₂

        plan_labels.append(row['plan'])
        cost_savings.append(monthly_cost_saving)
        emissions_savings.append(monthly_emissions_saving)

    # --- Graph for cost & emissions savings ---
    savings_fig = go.Figure()
    savings_fig.add_trace(go.Bar(x=plan_labels, y=cost_savings, name="Monthly Cost Savings ($)", marker_color="#3498db", yaxis="y", offsetgroup=0))
    savings_fig.add_trace(go.Bar(x=plan_labels, y=emissions_savings, name="Monthly Emissions Savings (kg CO₂)", marker_color="#e74c3c", yaxis="y2", offsetgroup=1))
    savings_fig.update_layout(
        title="Estimated Monthly Solar Savings by Plan",
        barmode="group",
        yaxis=dict(title="Cost Savings ($)", side="left"),
        yaxis2=dict(title="Emissions Savings (kg CO₂)", overlaying="y", side="right"),
        legend=dict(x=0.5, y=-0.3, xanchor="center", orientation="h"),
        margin=dict(t=50, b=100),
        plot_bgcolor="white"
    )

    # --- Graph for monthly solar output ---
    bar_fig = go.Figure(data=[
        go.Bar(x=list(calendar.month_abbr[1:]), y=monthly_kwh, marker_color="#7cc4b0")
    ])
    bar_fig.update_layout(
        title=f"Estimated Monthly Solar Output for ZIP {zip_code}",
        yaxis_title="kWh",
        plot_bgcolor="white"
    )

    ######## 20 year projection ########
    row = plan_details_df[plan_details_df['plan'] == selected_plan]

    years = list(range(1, 21))
    up_front_cost = 10626
    accum_cost_with = []
    accum_cost_without = []
    price_per_kwh = row['price_per_kwh'].values[0]

    for i in years:
        annual_cost_with = monthly_kwh_usage * price_per_kwh * 12 * (1 - (actual_coverage / 100) * (0.995 ** i)) * ((1.022 / 1.04) ** i)
        annual_cost_without = monthly_kwh_usage * price_per_kwh * 12 * ((1.022 / 1.04) ** i)

        if i == 1:
            accum_cost_with.append(annual_cost_with + up_front_cost)
            accum_cost_without.append(annual_cost_without)
        else:
            accum_cost_with.append(accum_cost_with[-1] + annual_cost_with)
            accum_cost_without.append(accum_cost_without[-1] + annual_cost_without)
        print(accum_cost_with)
        print(accum_cost_without)

    # Total savings over 20 years
    total_cost_with = accum_cost_with[-1]
    total_cost_without = accum_cost_without[-1]
    total_savings = total_cost_without - total_cost_with

    # Estimate payback year
    payback_year = None
    for y in range(20):
        if accum_cost_with[y] < accum_cost_without[y]:
            payback_year = y + 1  # Year number (1-indexed)
            break


    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=accum_cost_without, mode='lines+markers', name='Without Solar', line=dict(color="#e74c3c")))
    fig.add_trace(go.Scatter(x=years, y=accum_cost_with, mode='lines+markers', name='With Solar', line=dict(color="#3498db")))

    fig.update_layout(
        title=f"20-Year Accumulated Cost – {selected_plan}",
        xaxis_title="Year",
        yaxis_title="Cumulative Cost ($)",
        plot_bgcolor="white",
        margin=dict(t=50, b=100),
        legend=dict(x=0.5, y=-0.2, xanchor="center", orientation="h"),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=0.5,
            zeroline=False
        ),
        xaxis=dict(
            showgrid=False  # optional: keep x-axis clean
        )
    )


    return html.Div([
        warning_msg if warning_msg else None,
        
        dbc.Row([
            # Left: Cost & Emissions Savings Chart with heading
            dbc.Col(html.Div([
                html.H5(f"Estimated Monthly Solar Savings (Assuming {int(coverage_ratio * 100)}% Offset)"),
                dcc.Graph(figure=savings_fig)
            ]), width=6),

            # Right: Monthly Output Chart with heading
            dbc.Col(html.Div([
                html.H5(f"Estimated Annual Output: {int(annual_kwh)} kWh"),
                dcc.Graph(figure=bar_fig)
            ]), width=6),
        ], className="mb-4"),
        html.Hr(),
    ]), html.Div([
        html.Div([
            html.H5("Summary of Solar Impact", className="mt-4"),
            html.Ul([
                html.Li(f"Estimated Payback Year: {payback_year if payback_year else 'Beyond 20 years'}"),
                html.Li(f"Total 20-Year Savings: ${int(total_savings):,}")
            ], style={"fontSize": "14px"})
        ]),
        dcc.Graph(figure=fig, style={'width': '100%', 'height': '400px'}),
    ])

                   
if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)