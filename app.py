import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import json

# Load data
with open('data/zip_to_plan.json', 'r') as file:
    zip_to_plans = json.load(file)

plan_details_df = pd.read_csv('data/plan_details.csv')

app = dash.Dash(__name__)
app.title = "Residential Electrification Dashboard"

app.layout = html.Div([
    html.H1("Residential Electrification Dashboard", style={
        'textAlign': 'center',
        'marginBottom': '10px',
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

            html.Label("Plan for Pie Chart:", style={'fontWeight': 'bold', 'fontSize': '14px'}),
            dcc.Dropdown(id='plan_selector', placeholder='Select a plan',
                         style={'width': '100%', 'fontSize': '13px'}),

            html.Div(id='zip_warning', style={'color': 'red', 'marginTop': '5px', 'fontSize': '13px'})
        ], style={
            'width': '25%',
            'padding': '10px'
        }),

        # RIGHT: Graphs
        html.Div([
            dcc.Graph(id='plan_comparison', style={'height': '300px', 'marginBottom': '10px'}),
            dcc.Graph(id='power_mix_pie', style={'height': '260px'})
        ], style={'width': '75%', 'padding': '10px'})
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
    'overflow': 'hidden',
    'padding': '10px'
})

# Callback: Update bar chart + plan dropdown
@app.callback(
    [Output('plan_comparison', 'figure'),
     Output('plan_selector', 'options'),
     Output('plan_selector', 'value'),
     Output('zip_warning', 'children')],
    Input('zip_input', 'value'),
    Input('kwh_input', 'value'),
    Input('therms_input', 'value')
)
def update_bar_and_dropdown(zip_code, kwh_usage, therms_usage):
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

    fig.add_trace(go.Bar(
        x=plans['plan'],
        y=plans['price_per_kwh'] * kwh_usage,
        name='Monthly Cost ($)',
        marker_color='lightskyblue',
        yaxis='y',
        offsetgroup=0
    ))

    fig.add_trace(go.Bar(
        x=plans['plan'],
        y=plans['emissions_g_per_kwh'] * kwh_usage / 1000,
        name='Monthly Emissions (kg CO₂)',
        marker_color='lightcoral',
        yaxis='y2',
        offsetgroup=1
    ))

    fig.update_layout(
        title=f"Rate Plans for ZIP {zip_code}",
        width=700,
        barmode='group',
        yaxis=dict(title='Monthly Cost ($)', side='left'),
        yaxis2=dict(title='Monthly Emissions (kg CO₂)', overlaying='y', side='right'),
        legend=dict(x=0, y=1.05, yanchor="top", xanchor="left", orientation='h'),
        margin=dict(l=60, r=60, t=60, b=60)
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

    # Ordered sources: non-renewables first, then renewables
    power_sources = [
        "Coal", "Large Hydroelectric", "Natural Gas", "Nuclear", "Non-Renewable_Others", "Unspecified Power",
        "Biomass & Biowaste", "Geothermal", "Eligible Hydrelectric", "Solar", "Wind", "Renewable_Others"
    ]

    # Color scheme
    colors = [
        "#d73027", "#f46d43", "#fdae61", "#fee090", "#fdbb84", "#cccccc",  # Non-renewables
        "#91cf60", "#66bd63", "#1a9850", "#006837", "#2ca25f", "#a1d99b"   # Renewables
    ]

    row = plan_details_df[plan_details_df['plan'] == selected_plan].iloc[0]
    values = row[power_sources].astype(float).values

    pie_fig = go.Figure(data=[
        go.Pie(
            labels=power_sources,
            values=values,
            hole=0.4,
            marker=dict(colors=colors),
            name=selected_plan,
            sort=False,
            direction='clockwise',
            rotation=0
        )
    ])

    pie_fig.update_layout(
        title=f"Power Mix for {selected_plan}",
        width=700,
        height=400,
        margin=dict(l=60, r=60, t=60, b=60),
        legend=dict(orientation="h", y=-0.2)
    )

    return pie_fig

# Run app
if __name__ == '__main__':
    app.run(debug=True)
