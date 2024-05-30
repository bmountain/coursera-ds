# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# options
sites = list(spacex_df['Launch Site'].unique())
sites.insert(0, 'ALL')
options = []
for site in sites:
    options.append({'label': site, 'value': site})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown', 
                                    options = options, 
                                    value = 'ALL', 
                                    placeholder = 'Select a Lunach Site here', 
                                    searchable = True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider', 
                                    min = min_payload, 
                                    max = max_payload,
                                    step = 1000,
                                    value = [min_payload, max_payload]
                                    ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                               html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df, 
            values='class', 
        names='Launch Site', 
        title='Total Success Launches By Sites'
        )
        return fig
    else:
        # return the outcomes piechart for a selected site
        df_filter = spacex_df[spacex_df['Launch Site'] == entered_site].copy()
        df_group = df_filter.groupby('class').count().reset_index()
        df_site = df_group.iloc[:, :2].copy().rename({'Unnamed: 0': 'count'}, axis = 1)

        fig = px.pie(
            df_site, 
            values = 'count', 
            names = 'class', 
            title = f'Total Success Launches for {entered_site}'
            )
        return fig
        
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id = 'success-payload-scatter-chart', component_property = 'figure'),
    [
    Input(component_id = 'site-dropdown', component_property = 'value'),
    Input(component_id = 'payload-slider', component_property = 'value')
    ]
)
def get_scatter_plot(entered_site, entered_payload):
    min_slider, max_slider = entered_payload[0], entered_payload[1]
    df_range = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_slider) & (spacex_df['Payload Mass (kg)'] <= max_slider)].copy()
    if entered_site == 'ALL':
        fig = px.scatter(df_range, x = 'Payload Mass (kg)', y = 'class', color = 'Booster Version Category')
        return fig
    else:
        df_filter = df_range[df_range['Launch Site'] == entered_site].copy()
        fig = px.scatter(df_filter, x = 'Payload Mass (kg)', y = 'class', color = 'Booster Version Category')
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug = True, port = 8000)
