import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import json

# Load data
with open('data/zip_to_plan.json', 'r') as file:
    zip_to_plans = json.load(file)

plan_details_df = pd.read_csv('data/plan_details.csv')
gas_plan_details_df = pd.read_csv('data/gas_plan_details.csv')

app = dash.Dash(__name__)
app.title = "Residential Electrification Dashboard"

app.layout = html.Div([
    html.H1("Residential Electrification Dashboard", style={
        'textAlign': 'center',
        'marginBottom': '20px',
        'fontSize': '24px'
    }),

    html.Div([
        # LEFT: Inputs
        html.Div([
            html.Label("ZIP Code:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
            dcc.Input(id='zip_input', type='text', debounce=True, placeholder='e.g. 94301',
                      style={'width': '100%', 'marginBottom': '8px'}),

            html.Label("Electricity (kWh):", style={'fontWeight': 'bold', 'fontSize': '14px'}),
            dcc.Input(id='kwh_input', type='number', debounce=True, placeholder='e.g. 400', value=400,
                      style={'width': '100%', 'marginBottom': '8px'}),

            html.Label("Gas (therms):", style={'fontWeight': 'bold', 'fontSize': '14px'}),
            dcc.Input(id='therms_input', type='number', debounce=True, placeholder='e.g. 20', value=20,
                      style={'width': '100%', 'marginBottom': '8px'}),

            html.Label("Residential Gas Baseline Allowance (therms/day):", style={'fontWeight': 'bold', 'fontSize': '14px'}),
            dcc.Input(id='gas_allowance_input', type='number', debounce=True, placeholder='e.g. 1.3', value=1.3,
                      style={'width': '100%', 'marginBottom': '8px'}),

            html.Label("Plan for Pie Chart:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
            dcc.Dropdown(id='plan_selector', placeholder='Select a plan',
                         style={'width': '100%', 'fontSize': '13px'}),

            html.Div(id='zip_warning', style={'color': 'red', 'marginTop': '5px', 'fontSize': '13px'})
        ], style={
            'width': '15%',
            'padding': '5px',
            'boxSizing': 'border-box'
        }),

        # MIDDLE: Bar Chart
        html.Div([
            dcc.Graph(id='plan_comparison', style={'height': '500px'})
        ], style={
            'width': '40%', 
            'padding': '5px',
            'boxSizing': 'border-box'
        }),

        # RIGHT: Pie Chart
        html.Div([
            dcc.Graph(id='power_mix_pie', style={'height': '500px'})
        ], style={
            'width': '40%',
            'padding': '5px',
            'boxSizing': 'border-box'
        })
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'space-between',
        'alignItems': 'flex-start',
        'maxWidth': '1200px',
        'margin': '0 auto'
    })
], style={
    'fontFamily': 'Arial, sans-serif',
    'height': '100vh',
    'padding': '15px',
    'boxSizing': 'border-box'
})

# app.layout = html.Div([
#     html.H1("Residential Electrification Dashboard", style={
#         'textAlign': 'center',
#         'marginBottom': '10px',
#         'fontSize': '24px'
#     }),

#     html.Div([
#         # LEFT: Inputs
#         html.Div([
#             html.Label("ZIP Code:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
#             dcc.Input(id='zip_input', type='text', debounce=True, placeholder='e.g. 94301',
#                       style={'width': '100%', 'marginBottom': '8px'}),

#             html.Label("Electricity (kWh):", style={'fontWeight': 'bold', 'fontSize': '14px'}),
#             dcc.Input(id='kwh_input', type='number', debounce=True, placeholder='e.g. 400', value=400,
#                       style={'width': '100%', 'marginBottom': '8px'}),

#             html.Label("Gas (therms):", style={'fontWeight': 'bold', 'fontSize': '14px'}),
#             dcc.Input(id='therms_input', type='number', debounce=True, placeholder='e.g. 20', value=20,
#                       style={'width': '100%', 'marginBottom': '8px'}),

#             html.Label("Residential Gas Baseline Allowance (therms/day):", style={'fontWeight': 'bold', 'fontSize': '14px'}),
#             dcc.Input(id='gas_allowance_input', type='number', debounce=True, placeholder='e.g. 1.3', value=1.3,
#                       style={'width': '100%', 'marginBottom': '8px'}),

#             html.Label("Plan for Pie Chart:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
#             dcc.Dropdown(id='plan_selector', placeholder='Select a plan',
#                          style={'width': '100%', 'fontSize': '13px'}),

#             html.Div(id='zip_warning', style={'color': 'red', 'marginTop': '5px', 'fontSize': '13px'})
#         ], style={
#             'width': '15%',
#             'padding': '5px'
#         }),

#         # RIGHT: Graphs
#         html.Div([
#             dcc.Graph(id='plan_comparison', style={'height': '500px', 'marginBottom': '10px'}),
#             dcc.Graph(id='power_mix_pie', style={'height': '260px'})
#         ], style={'width': '85%', 'padding': '5px'})
#     ], style={
#         'display': 'flex',
#         'flexDirection': 'row',
#         'justifyContent': 'space-between',
#         'alignItems': 'flex-start',
#         'maxWidth': '1200px',
#         'margin': '0 auto'
#     })
# ], style={
#     'fontFamily': 'Arial, sans-serif',
#     'height': '100vh',
#     'overflow': 'hidden',
#     'padding': '10px'
# })

@app.callback(
    [Output('plan_comparison', 'figure'),
     Output('plan_selector', 'options'),
     Output('plan_selector', 'value'),
     Output('zip_warning', 'children')],
    Input('zip_input', 'value'),
    Input('kwh_input', 'value'),
    Input('therms_input', 'value'),
    Input('gas_allowance_input', 'value')
)
def update_bar_and_dropdown(zip_code, kwh_usage, therms_usage, gas_allowance):
    if not zip_code:
        return go.Figure(), [], None, ""

    zip_code = zip_code.strip()

    if zip_code not in zip_to_plans:
        return go.Figure(), [], None, f"No plans found for ZIP code {zip_code}."

    available_plans = zip_to_plans[zip_code]
    plans = plan_details_df[plan_details_df['plan'].isin(available_plans)]

    if plans.empty:
        return go.Figure(), [], None, f"No detailed plan information available for ZIP code {zip_code}."

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

    # Emissions bar (positioned to the right of the stacked bars)
    fig.add_trace(go.Bar(
        x=plans['plan'],
        y=plans['emissions_g_per_kwh'] * kwh_usage / 1000,
        name='Monthly Emissions (kg CO₂)',
        marker_color='#e74c3c',
        width=0.25,  # Narrower to fit beside costs
        offsetgroup='emissions',
        offset=0.15,  # Shift right to avoid overlap
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
            range=[0, max(plans['emissions_g_per_kwh'] * kwh_usage / 1000) * 1.2]  # Dynamic range for emissions
        ),
        legend=dict(
            x=0.5,
            y=-0.2,
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

    options = [{'label': plan, 'value': plan} for plan in plans['plan']]
    default_value = plans['plan'].iloc[0]

    return fig, options, default_value, ""

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
    pull = [0.1 if is_renewable[i] else 0 for i in range(len(combined_labels))]
    
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
            insidetextorientation='radial'
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
        annotations=[
            dict(
                text=f"{selected_plan}",
                x=0.5,
                y=0.5,
                font=dict(size=16, color='#505050'),
                showarrow=False,
                xanchor='center',
                yanchor='middle'
            )
        ],
        margin=dict(l=20, r=20, t=80, b=120),  # Increased bottom margin for legend
        height=550,  # Increased height to accommodate bottom legend
        legend=dict(
            orientation='h',  # Horizontal orientation
            x=0.5,
            y=-0.2,  # Position below the chart
            xanchor='center',
            yanchor='top',
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

# Run app
if __name__ == '__main__':
    app.run(debug=True)
