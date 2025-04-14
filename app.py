import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go

# Load rate plan data
rate_df = pd.read_csv('data/rate_plans_by_zip.csv')

app = dash.Dash(__name__)
app.title = "Residential Electrification Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Compare Electricity Plans by ZIP Code"),

    html.Label("Enter ZIP Code:"),
    dcc.Input(id='zip_input', type='text', debounce=True, placeholder='e.g. 94301'),

    html.Div(id='zip_warning', style={'color': 'red'}),
    dcc.Graph(id='plan_comparison')
])

# Callback
@app.callback(
    [Output('plan_comparison', 'figure'),
     Output('zip_warning', 'children')],
    Input('zip_input', 'value')
)
def update_graph(zip_code):
    if not zip_code:
        return go.Figure(), ""

    try:
        zip_code = int(zip_code)
    except ValueError:
        return go.Figure(), f"Invalid ZIP code: {zip_code}"

    plans = rate_df[rate_df['zip'] == zip_code]

    if plans.empty:
        return go.Figure(), f"No plans found for ZIP code {zip_code}."

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=plans['plan'],
        y=plans['price_per_kwh'],
        name='Cost ($/kWh)',
        marker_color='lightskyblue'
    ))

    fig.add_trace(go.Bar(
        x=plans['plan'],
        y=plans['emissions_g_per_kwh'],
        name='Emissions (g CO₂/kWh)',
        marker_color='lightcoral',
        yaxis='y2'
    ))

    fig.update_layout(
        title=f"Rate Plans for ZIP {zip_code}",
        yaxis=dict(title='Price ($/kWh)'),
        yaxis2=dict(
            title='Emissions (g CO₂/kWh)',
            overlaying='y',
            side='right'
        ),
        barmode='group',
        legend=dict(x=0, y=1.2, orientation='h')
    )

    return fig, ""

# Run app
if __name__ == '__main__':
    app.run(debug=True)