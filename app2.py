
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import json
import requests

# Load data
with open('data/zip_to_plan.json', 'r') as file:
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
    html.H1("Energy Rate Plan Comparison Dashboard", className='text-center mb-4'),
    
    # Main content container
    dbc.Container([
        dbc.Row([
            # Left sidebar with common inputs
            dbc.Col([
                html.Div([
                    html.H4("Consumption Profile", className='mb-3'),
                    
                    # Location input
                    html.Label("Zip Code"),
                    dbc.Input(id="zip_input", type="text", placeholder='e.g. 94301', value=None, className='mb-3'),
                    
                    # Electricity usage input
                    html.Label("Monthly Electricity Usage"),
                    dbc.InputGroup([
                        dbc.Input(id="kwh_input", type="number", placeholder="kWh", value=500),
                        dbc.InputGroupText("kWh"),
                    ], className='mb-3'),
                    
                    # Gas usage input
                    html.Label("Monthly Gas Usage"),
                    dbc.InputGroup([
                        dbc.Input(id="therms_input", type="number", placeholder="therms", value=25),
                        dbc.InputGroupText("therms"),
                    ], className='mb-3'),
                    
                    # Baseline allowance input
                    html.Label("Gas Baseline Allowance"),
                    dbc.InputGroup([
                        dbc.Input(id="gas_allowance_input", type="number", step="0.01", placeholder="therms/day", value=1.06),
                        dbc.InputGroupText("therms/day"),
                    ], className='mb-3'),
                    
                ], className='p-3 border rounded')
            ], width=2),
            
            # Main content area with tabs
            dbc.Col([
                html.Div([
                    # Tabs navigation
                    dbc.Tabs([
                        dbc.Tab(label="Base", tab_id="tab-base"),
                        dbc.Tab(label="Electrification Simulation", tab_id="tab-electrification"),
                        dbc.Tab(label="Solar Simulation", tab_id="tab-solar"),
                    ], id="tabs", active_tab="tab-base"),
                    
                    # Tab content container
                    html.Div(id="tab-content", className="pt-3")
                ])
            ], width=10)
        ])
    ], fluid=True),
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

                            # Fourth input
                            dbc.Col([
                                html.Label("Furnace Ratio (%):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='furnace_ratio_input', type='number', value=60, step=1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'})
                            ], width=2, className="px-1"),
                            
                            # Fifth input
                            dbc.Col([
                                html.Label("Water Heater Ratio (%):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='heater_ratio_input', type='number', value=60, step=1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'})
                            ], width=2, className="px-1"),
                            
                            # Sixth input
                            dbc.Col([
                                html.Label("Electrify (%):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='electrification_pct_input', type='number', value=100, step=1,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'})
                            ], width=2, className="px-1"),
                            
                            # Seventh input
                            dbc.Col([
                                html.Label("Solar (kW):", style={'fontWeight': 'bold', 'fontSize': '12px', 'marginBottom': '2px'}),
                                dcc.Input(id='solar_size_input', type='number', value=4, step=0.5,
                                        style={'width': '100%', 'height': '28px', 'padding': '2px'})
                            ], width=1, className="px-1"),
                        ], className="mb-3 g-0")
                        
                        # dbc.Row([
                        #     dbc.Col([
                        #         html.Label("Furnace Ratio (%):", style={'fontWeight': 'bold'}),
                        #         dcc.Input(id='furnace_ratio_input', type='number', value=60, step=1,
                        #                 style={'width': '100%'})
                        #     ], width=3),
                            
                        #     dbc.Col([
                        #         html.Label("Water Heater Ratio (%):", style={'fontWeight': 'bold'}),
                        #         dcc.Input(id='heater_ratio_input', type='number', value=60, step=1,
                        #                 style={'width': '100%'})
                        #     ], width=3),
                            
                        #     dbc.Col([
                        #         html.Label("Electrification %:", style={'fontWeight': 'bold'}),
                        #         dcc.Input(id='electrification_pct_input', type='number', value=100, step=1,
                        #                 style={'width': '100%'})
                        #     ], width=3),
                            
                        #     dbc.Col([
                        #         html.Label("Solar System Size (kW):", style={'fontWeight': 'bold'}),
                        #         dcc.Input(id='solar_size_input', type='number', value=4, step=0.5,
                        #                 style={'width': '100%'})
                        #     ], width=3)
                        # ])
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
            html.P("Content for the solar simulation tab will go here."),
            html.Div(id="solar-simulation-content", className="mt-4")
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

        # First: Electricity (bottom layer of stack)
        fig.add_trace(go.Bar(
            x=plans['plan'],
            y=electricity_costs,
            name='Electricity Cost',
            marker_color='#3498db',
            width=0.35,  # Slightly narrower to accommodate emissions bar
            offsetgroup='costs',
            offset=-0.2  # Shift left to make room for emissions
        ))

        # Second: Gas (stacked on top of electricity)
        fig.add_trace(go.Bar(
            x=plans['plan'],
            y=gas_costs,
            name='Gas Cost',
            marker_color='#e67e22',
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
            marker_color='#e74c3c',
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
            marker_color='navajowhite',
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
                x=0.5,
                y=-0.5,
                xanchor="center",
                yanchor="top",
                orientation='h',
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='lightgray',
                borderwidth=1,
                font=dict(size=14)
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
    Input('furnace_ratio_input', 'value'),
    Input('heater_ratio_input', 'value'),
    Input('electrification_pct_input', 'value'),
    Input('solar_size_input', 'value')
)
def update_bar_electrification(active_tab, zip_code, kwh_usage, therms_usage, gas_allowance,
                             cop, furnace_eff, heater_eff, furnace_ratio,
                             heater_ratio, electrification_pct, solar_size):
    if active_tab != "tab-electrification":
        raise dash.exceptions.PreventUpdate

    if not zip_code:
        return go.Figure(), [], None, ""

    zip_code = zip_code.strip()

    if zip_code not in zip_to_plans:
        return go.Figure(), [], None, f"No plans found for ZIP code {zip_code}."

    available_plans = zip_to_plans[zip_code]
    plans = plan_details_df[plan_details_df['plan'].isin(available_plans)]

    gas_emissions_factor = 5.3  # kg CO₂ per therm

    if plans.empty:
        return go.Figure()
    
    # --- Convert to decimals ---
    furnace_ratio /= 100
    heater_ratio /= 100
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
    emissions = []

    elec_colors = []
    gas_colors = []
    emission_colors = []
    emission_opacities = []

    for plan in plans['plan']:
        price_per_kwh = plans.loc[plans['plan'] == plan, 'price_per_kwh'].values[0]
        emissions_factor = plans.loc[plans['plan'] == plan, 'emissions_g_per_kwh'].values[0]

        # --- Original ---
        gas_base_orig = gas_base_price * min(therms_usage, gas_allowance * 30)
        gas_excess_orig = gas_excess_price * max(0, therms_usage - gas_allowance * 30)
        gas_total_orig = gas_base_orig + gas_excess_orig
        elec_cost_orig = price_per_kwh * kwh_usage
        emissions_kg_orig = emissions_factor * kwh_usage / 1000

        x_vals.append(plan + " (Original)")
        elec_costs.append(elec_cost_orig)
        gas_costs.append(gas_total_orig)
        emissions.append(emissions_kg_orig)
        elec_colors.append('lightblue')
        gas_colors.append('moccasin')
        emission_colors.append('lightcoral')
        emission_opacities.append(0.8)

        # --- Electrified ---
        gas_base_elec = gas_base_price * min(reduced_gas, gas_allowance * 30)
        gas_excess_elec = gas_excess_price * max(0, reduced_gas - gas_allowance * 30)
        gas_total_elec = gas_base_elec + gas_excess_elec
        elec_cost_elec = price_per_kwh * adjusted_kwh
        emissions_kg_elec = emissions_factor * adjusted_kwh / 1000

        x_vals.append(plan + " (Electrified)")
        elec_costs.append(elec_cost_elec)
        gas_costs.append(gas_total_elec)
        emissions.append(emissions_kg_elec)
        elec_colors.append('#3498db')
        gas_colors.append('#e67e22')
        emission_colors.append('#e74c3c')
        emission_opacities.append(0.9)

    # --- Add Electricity Bars ---
    fig.add_trace(go.Bar(
        x=x_vals,
        y=elec_costs,
        name='Electricity Cost',
        marker_color=elec_colors,
        width=0.35,
        offsetgroup='costs',
        offset=-0.2
    ))

    # --- Add Gas Bars ---
    fig.add_trace(go.Bar(
        x=x_vals,
        y=gas_costs,
        name='Gas Cost',
        marker_color=gas_colors,
        width=0.35,
        offsetgroup='costs',
        offset=-0.2
    ))

    # Separate emissions
    electric_emissions = []
    gas_emissions = []

    x_orig = []
    x_elec = []

    for plan in plans['plan']:
        emissions_factor = plans.loc[plans['plan'] == plan, 'emissions_g_per_kwh'].values[0]

        # Original emissions
        elec_em_orig = emissions_factor * kwh_usage / 1000
        gas_em_orig = gas_emissions_factor * therms_usage

        x_orig.append(plan + " (Original)")
        electric_emissions.append(elec_em_orig)
        gas_emissions.append(gas_em_orig)

        # Electrified emissions
        elec_em_elec = emissions_factor * adjusted_kwh / 1000
        gas_em_elec = gas_emissions_factor * reduced_gas

        x_elec.append(plan + " (Electrified)")
        electric_emissions.append(elec_em_elec)
        gas_emissions.append(gas_em_elec)

    # Electricity Emissions Bar
    fig.add_trace(go.Bar(
        x=x_orig + x_elec,
        y=electric_emissions,
        name='Electricity Emissions',
        marker_color='#e74c3c',
        width=0.25,
        offsetgroup='emissions',
        offset=0.15,
        yaxis='y2',
        opacity=0.85
    ))

    # Gas Emissions Bar
    fig.add_trace(go.Bar(
        x=x_orig + x_elec,
        y=gas_emissions,
        name='Gas Emissions',
        marker_color='navajowhite',
        width=0.25,
        offsetgroup='emissions',
        offset=0.15,
        yaxis='y2',
        opacity=0.85
    ))

    # --- Layout ---
    fig.update_layout(
        title={
            'text': f"Energy Rate Plans for ZIP {zip_code} (Electrification Simulation Enabled)",
            'font': {'size': 22, 'family': 'Arial, sans-serif'}
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
            'text': f"Power Mix for {selected_plan}<br><span style='font-size:14px;color:#2ca25f'>{renewable_pct}% Renewable</span> | <span style='font-size:14px;color:#d73027'>{non_renewable_pct}% Non-Renewable</span>",
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=18),
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


if __name__ == '__main__':
    app.run_server(debug=True)