
import pandas as pd
import dash
from dash import dcc, html, callback
import plotly.express as px
from dash.dependencies import Input, Output
import country_converter as cc


dash.register_page(__name__, path = '/Import.csv', name = "Import on the world", order = 11)


####################### DATA #############################

dataR = pd.read_csv(r"C:\Users\USER\Downloads\GlobalImpact-Covid19\data\Import.csv", sep=',', skiprows=4, header=None)
# link to the dataset: https://rshiny.ilo.org/dataexplorer0/?lang=en&segment=indicator&id=UNE_2EAP_SEX_AGE_RT_A
def load_process(data):
  column_names = data.iloc[0]
  data.columns = column_names
  data = data.drop(data.index[0])
  selected_columns = ['Country Name',2018.0, 2019.0, 2020.0, 2021.0, 2022.0, 2023.0]
  new_data = data[selected_columns]
  data.columns = data.columns.astype(str)
  value_vars = [col for col in data.columns[4:] if col != 'nan']
  melted_data = pd.melt(data, id_vars=['Country Name'], value_vars=value_vars, var_name='year', value_name='Import')
  melted_data['year'] = pd.to_numeric(melted_data['year'])
  filtered_data = melted_data[melted_data['year'].isin([2018,2019,2020, 2021, 2022, 2023])]
  unique_years = filtered_data['year'].unique()
  sorted_data = filtered_data.sort_values('Country Name')
  sorted_data = filtered_data.sort_values(['Country Name', 'year'])
  sorted_data['year'] = sorted_data['year'].astype(int)
  sorted_data = sorted_data.rename(columns={'Country Name': 'location'})
  sorted_data['continent'] = cc.convert(names=sorted_data['location'], to='continent')
  nan_count_continent = sorted_data['continent'].isnull().sum()
  nan_count_continent = sorted_data['Import'].isnull().sum()
  nan_counts_by_year = sorted_data.groupby('year')['Import'].apply(lambda x: x.isnull().sum())
  sorted_data = sorted_data[sorted_data['continent'] != 'not found']
  return sorted_data

def continent_Import(data):
  
  Import_by_continent_year = data.groupby(['continent', 'year'])['Import'].sum().reset_index()
  return Import_by_continent_year
def iso_country(data):
   
   data['iso_alpha'] = cc.convert(names=sorted_data['location'], to='ISO3')
   return data




# ####################### WIDGETS #############################

# Dropdown for 1
sorted_data=load_process(dataR)
data1=continent_Import(sorted_data)

data_columns1 = {
    "Import": data1["Import"],  
    "Year": data1["year"],
    "Continent": data1["continent"] }

categories1 = list(data_columns1.keys())

cat_dropdown1 = dcc.Dropdown(
    id="cat_column",
    options=categories1,
    value=categories1[0],  
    clearable=False
)
#graph id 1
graph1 = dcc.Graph(id="Import_graph1") 
# ####################### CHART #############################

def update_graph_continent(data):
    
    fig = px.line(data, x='year', y='Import', color='continent')
    fig.update_layout(title='Import by Continent and Year')
    return fig
# Dropdown for 2
sorted_data=load_process(dataR)
data2=iso_country(sorted_data)
data_columns2 = {
    "Import": data2["Import"],  
    "Year": data2["year"],
    "iso_alpha": data2["iso_alpha"] }

categories2 = list(data_columns2.keys())

cat_dropdown2 = dcc.Dropdown(
    id="cat_column",
    options=categories2,
    value=categories2[0],  
    clearable=False
)
# graph id 2
graph2 = dcc.Graph(id="Import_graph2") 
# ####################### CHART #############################

 


def plot_choropleth_map(data):
    fig = px.choropleth(
        data,
        locations="iso_alpha",
        color="Import",  
        hover_name="location",
        animation_frame="year", 
        color_continuous_scale=px.colors.sequential.Plasma,
        
    )
    return fig

    
        




# ####################### PAGE LAYOUT #############################

# Layout
layout = html.Div(children=[
    html.Br(),
    html.H2("Impact of Covid-19 on Import", className="fw-bold text-center"),
    html.Br(),
    html.Div([html.Label("Select Category for Graph 1"), cat_dropdown1]),
    html.Br(),
    graph1,
    html.Br(),
    html.Div([html.Label("Select Category for Graph 2"), cat_dropdown2]),
    html.Br(),
    graph2
])

# ####################### CALLBACKS ###############################

@callback(
    Output("Import_graph1", "figure"),  # Output for the first graph
    [Input("cat_column", "value")]  # Input from the first dropdown
)
def update_graph1(selected_category1):
    return update_graph_continent(data1)  # Pass the data1 as argument

@callback(
    Output("Import_graph2", "figure"),  # Output for the second graph
    [Input("cat_column", "value")]  # Input from the second dropdown
)
def update_graph2(selected_category2):
    return plot_choropleth_map(data2)  # Pass the data2 as argument


    




