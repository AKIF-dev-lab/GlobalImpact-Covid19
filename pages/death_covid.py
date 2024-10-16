import pandas as pd
import dash
from dash import dcc, html, callback
import plotly.express as px
from dash.dependencies import Input, Output
import country_converter as cc
import numpy as np
import pandas as pd
import sys
sys.path.insert(0,r'C:\Users\USER\Downloads\mock project\pages')
from GDP import load_and_process_gdp_data
# Register the page for multi-page Dash apps
dash.register_page(__name__, path='/relationship', name="GDP Analysis", order=3)

####################### DATASET #############################

# Load the data
data = pd.read_csv(r'C:\Users\USER\Downloads\mock project\data\owid-covid-data.csv', sep=',')
data_death=load_and_process_gdp_data()
# Keep only the necessary columns
columns_to_keep = ['continent', 'location', 'date', 'total_cases', 'total_deaths', 'population']
data = data[columns_to_keep]

# Creating a year column from date column
data['year'] = pd.to_datetime(data['date']).dt.year

# Get the last value per year for each location
last_value_per_year = data.groupby(['year', 'location'], as_index=False, sort=False).last()

# Drop the date column
data = last_value_per_year.drop(columns=['date'])

# Use the Country_converter to map the NAN values in continent with countries values
manual_mapping = {
    'Africa': 'Africa',
    'Asia': 'Asia',
    'Europe': 'Europe',
    'North America': 'North America',
    'Oceania': 'Oceania',
    'South America': 'South America',
}

nan_continent_rows = data['continent'].isnull()
continent_values = data.loc[nan_continent_rows, 'location'].apply(
    lambda x: cc.convert(names=x, to='continent', not_found=None)
)

data.loc[nan_continent_rows, 'continent'] = data.loc[nan_continent_rows, 'location'].map(
    manual_mapping
).fillna(pd.Series(continent_values, index=data.loc[nan_continent_rows, 'location'].index))

# Calculate the coefficient of variation for total_cases and total_deaths by continent
def coefficient_of_variation(group):
    std_dev = group.std()
    mean = group.mean()
    if mean == 0:
        return np.nan  # Handle cases where the mean is zero
    return std_dev / mean

continent_evolution_cases = data.groupby('continent')['total_cases'].apply(coefficient_of_variation)
continent_evolution_deaths = data.groupby('continent')['total_deaths'].apply(coefficient_of_variation)

continent_evolution_df = pd.DataFrame({
    'Coefficient_of_Variation_Cases': continent_evolution_cases,
    'Coefficient_of_Variation_Deaths': continent_evolution_deaths,
})

# Fill NaN values using continent evolution data

def replace_nan_with_continent_evolution(df, continent_evolution_df):
  df_copy = df.copy()  # Create a copy to avoid modifying the original DataFrame

  for column in ['total_cases', 'total_deaths']:
    for index, row in df_copy.iterrows():
      if pd.isnull(row[column]):
        continent = row['continent']
        if continent in continent_evolution_df.index:
          # Find the previous non-NaN value for the same location and year.
          previous_value = None
          for prev_index in range(index - 1, -1, -1):
            prev_row = df_copy.iloc[prev_index]
            if prev_row['location'] == row['location'] and prev_row['year'] == row['year'] and not pd.isnull(prev_row[column]):
              previous_value = prev_row[column]
              break

          if previous_value is not None:
            # Replace NaN with previous value multiplied by the coefficient of variation.
            df_copy.loc[index, column] = previous_value * continent_evolution_df.loc[continent, f'Coefficient_of_Variation_{column.split("_")[1]}']

          else:
            # Find the next non-NaN value for the same location and year.
            next_value = None
            for next_index in range(index + 1, len(df_copy)):
              next_row = df_copy.iloc[next_index]
              if next_row['location'] == row['location'] and next_row['year'] == row['year'] and not pd.isnull(next_row[column]):
                next_value = next_row[column]
                break
            if next_value is not None:
              # Replace NaN with next value divided by the coefficient of variation.
              df_copy.loc[index, column] = next_value / continent_evolution_df.loc[continent, f'Coefficient_of_Variation_{column.split("_")[1]}']
  return df_copy




data_filled = replace_nan_with_continent_evolution(data, continent_evolution_df)

# Remove specific locations
names_to_remove = ['Hong Kong', 'Western Sahara']
data = data[~data['location'].isin(names_to_remove)]

# Remove 2024 data
data_death = data[data['year'] != 2024]
# Get the GDP data
gdp_data = load_and_process_gdp_data() 

# Merge the dataframes
merged_data = pd.merge(data_death, gdp_data[['location', 'year', 'GDP']],  # Select specific columns
                      on=['location', 'year'], 
                      how='left') 

# Define the layout of the Dash app
layout = html.Div(children=[
    html.H1(children="GDP Analysis"),

    html.Div(children='''
        Explore the relationship between GDP and COVID-19 cases and deaths.
    '''),

    dcc.Graph(id='gdp-graph'),

    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': year, 'value': year} for year in data['year'].unique()],
        value=data['year'].min()  # Set the default value to the minimum year
    ),
])


####################### Plot ################################



def graph_deathbycountry():
    fig = px.scatter(merged_data, 
                     x='total_deaths', 
                     y='GDP', 
                     color='year',
                     hover_name='location', 
                     )
    fig.update_layout(transition_duration=500)
    return fig


def graph_deathbycontinent():
    fig = px.scatter(merged_data, 
                     x='total_deaths', 
                     y='GDP', 
                     color='year',
                     hover_name='continent', 
                     )
    fig.update_layout(transition_duration=500)
    return fig
