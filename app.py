import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import json
import os

# Load data
with open('data/zip_to_plan.json', 'r') as file:
    zip_to_plans = json.load(file)

plan_details_df = pd.read_csv('data/plan_details.csv')

app = dash.Dash(__name__)
app.title = "Residential Electrification Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Compare Electricity Plans by ZIP Code"),

    html.Label("Enter ZIP Code:"),
    dcc.Input(id='zip_input', type='text', debounce=True, placeholder='e.g. 94301'),

    html.Label("Enter Monthly Electricity Usage (kWh):"),
    dcc.Input(id='kwh_input', type='number', debounce=True, placeholder='e.g. 400', value=400), 

    html.Label("Enter Monthly Gas Usage (therms):"),
    dcc.Input(id='therms_input', type='number', debounce=True, placeholder='e.g. 20', value=20),

    html.Div(id='zip_warning', style={'color': 'red'}),
    dcc.Graph(id='plan_comparison')
])

# Callback
@app.callback(
    [Output('plan_comparison', 'figure'),
     Output('zip_warning', 'children')],
    Input('zip_input', 'value'),
    Input('kwh_input', 'value'),
    Input('therms_input', 'value')
)
def update_graph(zip_code, kwh_usage, therms_usage):
    if not zip_code:
        return go.Figure(), ""

    zip_code = zip_code.strip()

    if zip_code not in zip_to_plans:
        return go.Figure(), f"No plans found for ZIP code {zip_code}."

    # Get plans for this ZIP code
    available_plans = zip_to_plans[zip_code]
    plans = plan_details_df[plan_details_df['plan'].isin(available_plans)]

    if plans.empty:
        return go.Figure(), f"No detailed plan information available for ZIP code {zip_code}."

    fig = go.Figure()

    # Cost bar (left axis)
    fig.add_trace(go.Bar(
        x=plans['plan'],
        y=plans['price_per_kwh'] * kwh_usage,
        name='Monthly Cost ($)',
        marker_color='lightskyblue',
        yaxis='y',
        offsetgroup=0  # group for alignment
    ))

    # Emissions bar (right axis)
    fig.add_trace(go.Bar(
        x=plans['plan'],
        y=plans['emissions_g_per_kwh'] * kwh_usage / 1000,  # optional: convert to kg
        name='Monthly Emissions (kg CO₂)',
        marker_color='lightcoral',
        yaxis='y2',
        offsetgroup=1  # separate offset group
    ))

    fig.update_layout(
        title=f"Rate Plans for ZIP {zip_code}",
        width=700,
        barmode='group',
        yaxis=dict(
            title='Monthly Cost ($)',
            side='left'
        ),
        yaxis2=dict(
            title='Monthly Emissions (kg CO₂)',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            x=0,
            y=1.05,
            yanchor="top",
            xanchor="left",
            orientation='h'
        ),
        margin=dict(l=60, r=60, t=60, b=60)
    )


    return fig, ""

# Run app
if __name__ == '__main__':
    app.run(debug=True)