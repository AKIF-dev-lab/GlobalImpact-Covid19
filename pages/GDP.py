import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import country_converter as cc

# Load your data (same as in your notebook)
data = pd.read_csv(r'C:\Users\USER\Downloads\mock project\data\API_NY.GDP.MKTP.KD.ZG_DS2_en_csv_v2_31631.csv', sep=',', skiprows=4, header=None)
column_names = data.iloc[0]
data.columns = column_names
data = data.drop(data.index[0])


# Select necessary columns
selected_columns = ['Country Name',2018.0, 2019.0, 2020.0, 2021.0, 2022.0, 2023.0]
new_data = data[selected_columns]

# Melt the data
melted_data = pd.melt(data, id_vars=['Country Name'], value_vars=data.columns[4:], var_name='year', value_name='GDP')
melted_data['year'] = pd.to_numeric(melted_data['year'])

# Filter by years
filtered_data = melted_data[melted_data['year'].isin([2018,2019,2020, 2021, 2022, 2023])]

# Sort the data
data_gdp = filtered_data.sort_values(['Country Name', 'year'])
data_gdp['year'] = data_gdp['year'].astype(int)
sorted_data = data_gdp.rename(columns={'Country Name': 'location'})
sorted=sorted_data.copy()
sorted['continent'] = cc.convert(names=sorted_data['location'], to='continent')
print(sorted)
def load_gdp_data():
  return sorted
#Adding a column of continent converted from countries columns

# Create a Dash app layout
def create_layout():
    return html.Div([
        dcc.Graph(id='gdp-graph'),
    ])

# Create the graph
def update_graph():
    fig = px.line(sorted, x='year', y='GDP', color='Continent')
    return fig




def update_graph_callback(input_value):
    return update_graph()


