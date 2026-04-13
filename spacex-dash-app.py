# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# 1. Cargar datos
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Crear opciones para el dropdown dinámicamente
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

app = dash.Dash(__name__)

# 2. Layout: El esqueleto de tu app
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Range Slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Scatter Chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# --- CALLBACKS ---

# Callback para el Pie Chart (TASK 2)
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class', 
                     names='Launch Site', 
                     title='Total Success Launches By Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        df_site = filtered_df.groupby(['class']).size().reset_index(name='count')
        fig = px.pie(df_site, values='count', 
                     names='class', 
                     title=f'Total Success Launches for site {entered_site}')
    return fig

# Callback para el Scatter Chart (TASK 4)
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'), 
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    df_filtered = spacex_df[mask]

    if entered_site == 'ALL':
        fig = px.scatter(
            df_filtered, x="Payload Mass (kg)", y="class",
            color="Booster Version Category",
            title="Correlation between Payload and Success for all Sites"
        )
    else:
        df_site_filtered = df_filtered[df_filtered['Launch Site'] == entered_site]
        fig = px.scatter(
            df_site_filtered, x="Payload Mass (kg)", y="class",
            color="Booster Version Category",
            title=f"Correlation between Payload and Success for site {entered_site}"
        )
    return fig

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)