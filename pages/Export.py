# Import necessary libraries
import pandas as pd
import dash
from dash import dcc, html, callback
import plotly.express as px
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import country_converter as cc
import plotly.graph_objects as go


# Register the page for the dashboard
dash.register_page(__name__, path='/Export.csv', name="Export on the world", order=11)

####################### DATA LOADING AND PROCESSING #############################

# Load Export data
dataR = pd.read_csv(r"C:\Users\USER\Downloads\GlobalImpact-Covid19\data\Export.csv", sep=',', skiprows=4, header=None)

# Load Manufacturing data
dataM = pd.read_csv(r"C:\Users\USER\Downloads\GlobalImpact-Covid19\data\manufacturing.csv", sep=',', skiprows=4, header=None)

# Function to process Export data

def load_process_export(data):
    column_names = data.iloc[0]
    data.columns = column_names
    data = data.drop(data.index[0])
    
    # Keep necessary columns
    selected_columns = ['Country Name', 2018.0, 2019.0, 2020.0, 2021.0, 2022.0, 2023.0]
    data = data[selected_columns]
    
    # Rename columns for easier access
    data.columns = data.columns.astype(str)
    data = data.rename(columns={'Country Name': 'location'})
    
    # Calculate the difference between 2020 and 2019 for each country
    data['diff_2020_2019_export'] = data['2020.0'] - data['2019.0']
    
    # Melt the dataframe to long format for year-based analysis
    value_vars = ['2018.0', '2019.0', '2020.0', '2021.0', '2022.0', '2023.0']
    melted_data = pd.melt(data, id_vars=['location', 'diff_2020_2019_export'], value_vars=value_vars, var_name='year', value_name='Export')
    
    # Convert year column to numeric
    melted_data['year'] = pd.to_numeric(melted_data['year'])
    
    # Sort data by location and year
    melted_data = melted_data.sort_values(['location', 'year'])
    melted_data['year'] = melted_data['year'].astype(int)
    
    # Add continent information
    melted_data['continent'] = cc.convert(names=melted_data['location'], to='continent')
    
    # Filter out rows where continent is not found
    melted_data = melted_data[melted_data['continent'] != 'not found']
    
    return melted_data


# Function to process Manufacturing data and calculate the difference between 2020 and 2019
def load_process_manufacturing(data):
    column_names = data.iloc[0]
    data.columns = column_names
    data = data.drop(data.index[0])
    
    # Keep necessary columns
    selected_columns = ['Country Name',  2019.0, 2020.0]
    data = data[selected_columns]
    
    # Rename columns for easier access
    data.columns = data.columns.astype(str)
    data = data.rename(columns={'Country Name': 'location'})
    
    # Calculate the difference between 2020 and 2019 for each country
    data['diff_2020_2019_manufacturing'] = data['2020.0'] - data['2019.0']
    
    # Melt the dataframe to long format for year-based analysis
    value_vars = [ '2019.0', '2020.0']
    melted_data = pd.melt(data, id_vars=['location', 'diff_2020_2019_manufacturing'], value_vars=value_vars, var_name='year', value_name='Manufacturing')
    
    # Convert year column to numeric
    melted_data['year'] = pd.to_numeric(melted_data['year'])
    
    # Sort data by location and year
    melted_data = melted_data.sort_values(['location', 'year'])
    melted_data['year'] = melted_data['year'].astype(int)
    
    # Add continent information
    melted_data['continent'] = cc.convert(names=melted_data['location'], to='continent')
    
    # Filter out rows where continent is not found
    melted_data = melted_data[melted_data['continent'] != 'not found']
    
    return melted_data
def iso_country(data):
   
   data['iso_alpha'] = cc.convert(names=data['location'], to='ISO3')
   return data

# Process the data for export and manufacturing
sorted_data_export = load_process_export(dataR)
sorted_data_manufacturing = load_process_manufacturing(dataM)

# Grouping Export by continent and year
data1 = sorted_data_export.groupby(['continent', 'year'])['Export'].sum().reset_index()
data2=iso_country(sorted_data_export)

data2_M=iso_country(sorted_data_manufacturing)
# Grouping Manufacturing by continent and year
dataM_by_continent = sorted_data_manufacturing.groupby(['continent', 'year'])['Manufacturing'].sum().reset_index()

# Process the data
export_diff_data = data2[['iso_alpha','location', 'diff_2020_2019_export']]

manufacturing_diff_data = data2_M[['iso_alpha','location',  'diff_2020_2019_manufacturing']]

# Merge the two datasets
combined_data = pd.merge(export_diff_data, manufacturing_diff_data, on=['iso_alpha','location'], how='inner')
####################### WIDGETS AND GRAPHS #############################

# Dropdown and graph for Export data
data_columns1 = {
    "Export": data1["Export"],
    "Year": data1["year"],
    "Continent": data1["continent"]}
categories1 = list(data_columns1.keys())
cat_dropdown1 = dcc.Dropdown(id="cat_column1", options=categories1, value=categories1[0], clearable=False)
graph1 = dcc.Graph(id="Export_graph1")

# Dropdown and graph for Export Choropleth
data_columns2 = {
    "Export": data2["Export"],
    "Year": data2["year"],
    "iso_alpha": data2["iso_alpha"]}
categories2 = list(data_columns2.keys())
cat_dropdown2 = dcc.Dropdown(id="cat_column2", options=categories2, value=categories2[0], clearable=False)
graph2 = dcc.Graph(id="Export_graph2")

# Dropdown and graph for Difference
data_columns3 = {
    'diff_2020_2019_export': combined_data['diff_2020_2019_export'],
    'diff_2020_2019_manufacturing': combined_data['diff_2020_2019_manufacturing'],
    "iso_alpha": combined_data["iso_alpha"]
    
}

# Create categories3 from data_columns3 keys
categories3 = list(data_columns3.keys())

# Dropdown and graph for the Third Graph
cat_dropdown3 = dcc.Dropdown(
    id="cat_column3",
    options=[{'label': value, 'value': key} for key, value in data_columns3.items()],
    value=categories3[0],  # Default value (first category)
    clearable=False
)

# Graph for showing the third graph
graph3 = dcc.Graph(id="diff_graph3")

####################### PLOTTING FUNCTIONS #############################

# Line plot for Export data
def update_graph_continent_export(data):
    fig = px.line(data, x='year', y='Export', color='continent')
    fig.update_layout(title='Export by Continent and Year')
    return fig

# Choropleth map for Export data
def plot_choropleth_export(data):
    fig = px.choropleth(
        data,
        locations="iso_alpha",
        color="Export",
        hover_name="location",
        animation_frame="year",
        color_continuous_scale=px.colors.sequential.Plasma
    )
    return fig

# Choropleth map for difference
# Function to plot choropleth map for differences
def plot_choropleth_differences(data):
    fig = px.choropleth(
        data,
        locations="iso_alpha",
        color="diff_2020_2019_export",  # Default to export differences
        hover_name="location",
        
        color_continuous_scale=px.colors.sequential.Plasma,
        title='Choropleth Map for Export Differences'
    )
    
    # Add a second color scale for manufacturing differences
    fig.add_trace(px.choropleth(
        data,
        locations="iso_alpha",
        color="diff_2020_2019_manufacturing",  # Add manufacturing differences
        hover_name="location",
        
        color_continuous_scale=px.colors.sequential.Plasma,
        title='Choropleth Map for Manufacturing Differences'
    ).data[0])  # Using the first trace

    return fig


####################### PAGE LAYOUT #############################
layout = html.Div(children=[
    html.Br(),
    html.H2("Impact of Covid-19 on export", className="fw-bold text-center"),
    html.Br(),
    html.Div([html.Label("Select Category for Graph 1"), cat_dropdown1]),
    html.Br(),
    graph1,
    html.Br(),
    html.Div([html.Label("Select Category for Graph 2"), cat_dropdown2]),
    html.Br(),
    graph2,
    html.Br(),
    html.Div([html.Label("Select Category for Graph 2"), cat_dropdown3]),
    html.Br(),
    graph3
])
# Define the layout for all three graphs
#################### CALLBACKS #############################

# Callback for updating Export line graph
@callback(
    Output("Export_graph1", "figure"),
    [Input("cat_column1", "value")]
)
def update_graph1(categories1):
    return update_graph_continent_export(data1)

# Callback for updating Export choropleth graph
@callback(
    Output("Export_graph2", "figure"),
    [Input("cat_column2", "value")]
)
def update_graph2(categories2):
    return plot_choropleth_export(data2)

# Callback for updating Manufacturing line graph

@callback(
    Output("difference-graph", "figure"),
    [Input("cat_column3", "value")]
)
def update_difference_graph(selected_category):
    # Call the plot function with the combined data
    fig = plot_choropleth_differences(combined_data)
    return fig
