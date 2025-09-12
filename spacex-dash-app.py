# spacex_dash_app.py
# ------------------
# SpaceX Launch Records Dashboard

import os
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Column names used below (adjust here if your file uses different names)
COL_LAUNCH_SITE = "Launch Site"
COL_CLASS = "class"
COL_PAYLOAD = "Payload Mass (kg)"
COL_BOOSTER = "Booster Version Category"

# Payload bounds for slider defaults
max_payload = spacex_df[COL_PAYLOAD].max()
min_payload = spacex_df[COL_PAYLOAD].min()

# Create Dash app
app = dash.Dash(__name__)

# Dropdown options (All + unique sites)
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': s, 'value': s} for s in sorted(spacex_df[COL_LAUNCH_SITE].unique())
]

# Layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Payload range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 10001, 2500)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Scatter chart
    html.Br(),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Pie chart callback
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(selected_site):
    df = spacex_df.copy()

    if selected_site == 'ALL':
        # total successful launches per site (class == 1)
        df_success = df[df[COL_CLASS] == 1]
        success_by_site = (
            df_success.groupby(COL_LAUNCH_SITE)[COL_CLASS]
            .count()
            .reset_index(name='success_count')
        )
        fig = px.pie(
            success_by_site,
            names=COL_LAUNCH_SITE,
            values='success_count',
            title='Total Successful Launches by Site'
        )
        return fig
    else:
        # site-specific success vs failure counts
        site_df = df[df[COL_LAUNCH_SITE] == selected_site]
        counts = site_df[COL_CLASS].value_counts().reindex([1, 0], fill_value=0)
        fig = px.pie(
            names=['Success', 'Failure'],
            values=[counts[1], counts[0]],
            title=f'Success vs Failure for {selected_site}'
        )
        return fig

# TASK 4: Scatter chart callback
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range

    # filter by payload
    df = spacex_df[
        (spacex_df[COL_PAYLOAD] >= low) &
        (spacex_df[COL_PAYLOAD] <= high)
    ]

    # filter by site unless ALL
    title = 'Payload vs. Outcome for All Sites'
    if selected_site != 'ALL':
        df = df[df[COL_LAUNCH_SITE] == selected_site]
        title = f'Payload vs. Outcome for {selected_site}'

    fig = px.scatter(
        df,
        x=COL_PAYLOAD,
        y=COL_CLASS,
        color=COL_BOOSTER,
        hover_data=[COL_LAUNCH_SITE, 'Flight Number'] if 'Flight Number' in df.columns else [COL_LAUNCH_SITE],
        title=title,
        labels={COL_CLASS: 'Outcome (1=Success, 0=Failure)'}
    )
    fig.update_yaxes(tickmode='array', tickvals=[0, 1], range=[-0.2, 1.2])
    return fig

# Run the app (bind to 0.0.0.0 and use Cloud IDE port if provided)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host='0.0.0.0', port=port, debug=False)
