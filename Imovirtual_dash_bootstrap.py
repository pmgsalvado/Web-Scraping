import os
import dash
import pandas as pd
import numpy as np
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import imovirtual_webscrapping_v2
# this is a library necessary to generate maps
import folium
from folium import plugins
import external_functions




# ----------------------- // -----------------------
# The rest of the code

# Unccoment the read fresh information from the site - normal use
#dataframe = imovirtual_webscrapping_v2.main()
#dataframe.to_csv('imovirtual_df_no_outliers.csv', index=False)

# uncomment or comment for developing purposes to use local data
#dataframe = pd.read_csv('imovirtual_df_no_outliers.csv')
dataframe = pd.read_csv('imovirtual.csv')


# first operation
dataframe = dataframe.sort_values(by='Typology')
print(dataframe.shape)

# print(dataframe.dtypes)
# ----------------------- /General Variables/ -----------------------

cities = dataframe['City'].unique().tolist()
cities.append('All')
area_max = dataframe['Area (m²)'].max()
area_min = dataframe['Area (m²)'].min()
price_max = dataframe['Price (€/month)'].max()
price_min = dataframe['Price (€/month)'].min()

# -----------------------/ Generate Map / -----------------------------
map_ = folium.Map(location=[38.7452, -9.1604], zoom_start=5)
map_.save('portugal_map.html')

# create a dash application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# app = dash.Dash(__name__)
# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# ----------------------- /Styling/ -----------------------
style_img = {'display': 'block',
             'margin-left': 'auto',
             'margin-right': 'auto',
             'width': '50%'}

style_general = {'background-color': '#152238',
                 #'margin-left': '5px',
                 #'margin-right': '5px',
                 }

font_color = {'color': '#008000'}

style_general_graph = {'background-color': '#23395d',
                       'margin-left': '5px',
                       'margin-right': '5px',
                       'width': '33%',
                       'heigth': 'auto'}

style_dropdown = {'background-color': '#152238',
                  'margin-left': '5px',
                  'margin-right': '5px',
                  'color': '#008000',
                  'align': 'center'
                  }

style_table = {'margin-left': 'auto',
               'margin-right': 'auto',
               'border-spacing': '100px',
               'textAlign': 'center',
               'width': '40%',
               'color': '#008000'}
# ----------------------- // -----------------------

app.layout = dbc.Container([
    html.Img(src='https://www.imovirtual.com/frontera/static/media/logo.8035707c.svg'),
    html.H1('Web Scraping Imovirtual House', className='text-primary'),

    dbc.Container([
        html.H4('Select a City', className="text-start text-primary"),
        html.Div(dcc.Dropdown(cities, 'All', id='cities', placeholder='Select a City')),
        html.H4('Select an Area Range', className="text-start text-primary"),
        html.Div(dcc.RangeSlider(max=area_max, min=area_min, step=2,
                                 id='area_slider', dots=False,
                                 value=[area_min, area_max], marks={str(area_min): {'label': '0'},
                                                                    str(area_max): {'label': '100'}}
                                 )),
        html.P(''),
        html.H4('Select a Price Range', className="text-start text-primary"),
        html.Div(dcc.RangeSlider(max=price_max, min=price_min, step=5,
                                 id='price_slider', dots=False,
                                 value=[price_min, price_max],
                                 marks={price_min: str(price_min),
                                        price_max: str(price_max)},
                                 )),

    ], className="bg-light"),

    # Overall Information
    dbc.Container([
        html.H5('Total Houses Found', className='text-center text-primary'),
        html.H5('1650', id='total-houses', className='text-center text-primary text-decoration-underline ')
    ]),

    # Table information
    dbc.Container([
        html.Table(children=[
            html.Tr(children=[
                html.Th('Minimum Price'),
                html.Th('Maximum Price'),
            ]),
            html.Tr(children=[
                html.Td(id='min-price'),
                html.Td(id='max-price'),
            ]),
        ], className='table text-primary'),
    ]),

    # Graph Section

    dbc.Container([
        html.Div([
        # Plot Histogram Typology vs Count per Typology
        html.Div([], id='hist_graph', className='col'),
        # Plot Box Plot by Typology vs Price
        html.Div([], id='box_graph', className='col'),
        # Plot histogram displaying areas
        html.Div([], id='area_graph', className='col'),
        ], className='row')
    ], className='container'),
    # Map
    dbc.Container([
        html.Iframe(id='map', srcDoc=open('portugal_map.html', 'r').read(), width='80%', height='600')
    ]),

    dbc.Container([
        html.H5('Small Example of Web scraping - Plotly Dash and Bootstrap', className='text-center text-primary'),
        html.H6('by Pedro Salvado', className='text-center text-primary')
    ], className='border-top')
], className="text-center container-xl", style={'background-color': '#152238'})


# ----------------------- /   CallBacks   / -----------------------


@app.callback([Output(component_id='hist_graph', component_property='children'),
               Output(component_id='box_graph', component_property='children'),
               Output(component_id='area_graph', component_property='children'),
               Output(component_id='map', component_property='srcDoc')
               ],
              [Input(component_id='cities', component_property='value'),
               Input(component_id='area_slider', component_property='value'),
               Input(component_id='price_slider', component_property='value')])
def city(value, area_, price_):
    # filtering part of the data frame according to area range and price range, defined in the range slider
    dataframe_ = dataframe[(dataframe['Area (m²)'] >= area_[0]) & (dataframe['Area (m²)'] <= area_[1])]
    dataframe_ = dataframe_[(dataframe_['Price (€/month)'] >= price_[0]) & (dataframe_['Price (€/month)'] <= price_[1])]
    if value == 'All':

        hist_graph = px.histogram(data_frame=dataframe_,
                                  x='Typology',
                                  color='Typology'
                                  )

        box_graph = px.box(data_frame=dataframe_,
                           x='Typology',
                           y='Price (€/month)',
                           color='Typology')
        area_graph = px.histogram(data_frame=dataframe_,
                                  x='Area (m²)',
                                  nbins=15,
                                  pattern_shape='Typology', color='Typology')

        #folium map function call
        map_portugal = generate_map(dataframe_['Latitude'], dataframe_['Longitude'])
    else:
        dataframe_filtered = dataframe_[dataframe_['City'] == value]
        hist_graph = px.histogram(data_frame=dataframe_filtered,
                                  x='Typology',
                                  color='Typology',
                                  )

        box_graph = px.box(data_frame=dataframe_filtered,
                           x='Typology',
                           y='Price (€/month)',
                           color='Typology')
        area_graph = px.histogram(data_frame=dataframe_filtered,
                                  x='Area (m²)',
                                  nbins=15,
                                  pattern_shape='Typology',  color='Typology')

        map_portugal = generate_map(dataframe_filtered['Latitude'], dataframe_filtered['Longitude'])

    hist_graph.update_layout(title={'text': 'CountPlot Histogram', 'x': 0.5},
                             paper_bgcolor=style_general_graph['background-color'], font_color='#008000')
    hist_graph.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)'})

    box_graph.update_layout(title={'text': 'BoxPlot Typology vs Price', 'x': 0.5},
                            paper_bgcolor=style_general_graph['background-color'], font_color='#008000')
    box_graph.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)'})
    area_graph.update_layout(title={'text': 'Histogram Area vs Price', 'x': 0.5},
                             paper_bgcolor=style_general_graph['background-color'], font_color='#008000', )
    area_graph.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)'})

    # return hist_graph
    return [dcc.Graph(figure=hist_graph),
            dcc.Graph(figure=box_graph),
            dcc.Graph(figure=area_graph),
            map_portugal]


@app.callback(Output(component_id='area', component_property='children'),
              Input(component_id='area_slider', component_property='value'))
def area(value):
    return f'Area Min: {value[0]} - Area Max: {value[1]}'


@app.callback(Output(component_id='price', component_property='children'),
              Input(component_id='price_slider', component_property='value'))
def price(value):
    return f'Price Min: {value[0]} - Price Max: {value[1]}'


def generate_map(latitude: list, longitude: list):
    portugal_map = folium.Map(location=[38.7452, -9.1604], zoom_start=5)
    cities_map = plugins.MarkerCluster().add_to(portugal_map)

    list_coordinates = []
    for lat, long in zip(latitude, longitude):
        # print(lat, long)
        if [lat, long] == [np.nan, np.nan]:
            continue
        else:
            folium.Marker(location=[lat, long],
                          icon=None,
                          popup=None).add_to(cities_map)

    portugal_map.save('portugal_map.html')
    return open('portugal_map.html', 'r').read()


@app.callback([Output(component_id='total-houses', component_property='children'),
               Output(component_id='max-price', component_property='children'),
               Output(component_id='min-price', component_property='children')],
              [Input(component_id='area_slider', component_property='value'),
               Input(component_id='price_slider', component_property='value'),
               Input(component_id='cities', component_property='value')])
def general_info(area_, price_, cities_):
    dataframe_ = dataframe[(dataframe['Area (m²)'] >= area_[0]) & (dataframe['Area (m²)'] <= area_[1])]
    dataframe_ = dataframe_[(dataframe_['Price (€/month)'] >= price_[0]) & (dataframe_['Price (€/month)'] <= price_[1])]
    if cities_ != 'All':
        dataframe_ = dataframe_[dataframe_['City'] == cities_]
    total_houses = dataframe_.shape[0]
    max_price = dataframe_['Price (€/month)'].max()
    min_price = dataframe_['Price (€/month)'].min()
    return [total_houses, max_price, min_price]


# Run Application
if __name__ == '__main__':
    app.run_server(debug=True)
