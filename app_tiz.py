import streamlit as st
from urllib.request import urlopen
import json
from datetime import datetime
import pandas as pd
import plotly.express as px

def page():
    
    st.title('Zone colore dell\'Italia')

    st.markdown('''
        Dal 22 novembre 2020 l'emergenza Covid in Italia è stata gestita in una suddivisione in zone di colore, dipendenti dall'indice Rt calcolato in ogni regione.

        In questa pagina è possibile selezionare una data per vederne la situazione nazionale. Per il calcolo dell'indice Rt si rimanda alla pagina apposita.
    ''')
        
    with open('./data/limits_IT_regions.geojson') as confini:
        italy_regions_geo = json.load(confini)
    df = pd.read_csv("data/zone_regioni_esteso.csv")
    date = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f") for d in  df["data_inizio"]]
    df["data"] = date
    color_discrete_map = {'unknown':  'rgb(1,0,0)', 'bianca': 'lightblue', 'gialla': 'yellow', 'arancione': 'orange','rossa': 'red'}

    input_date = st.date_input('Seleziona una data:')
    selected_date = input_date.strftime("%Y-%m-%d %H:%M:%S.%f")
    map_df = df[df["data"]==selected_date]

    start_date = "2020-11-22 00:00:00.0" 

    if selected_date < start_date:
        st.error('Non sono presenti dati di zona per la data inserita. Inserire un\'altra data.')
    else:
        fig = px.choropleth_mapbox(data_frame=map_df, 
                    locations='regione',                    # dataframe column to match with featureidkey
                    geojson=italy_regions_geo,              # geojson
                    featureidkey='properties.reg_name',     # path of the geojson field to match with locations
                    color="zona",                           # colonna df a cui fare l'assegnazione colore
                    color_discrete_map=color_discrete_map,  # color map defined above
                    center = {"lat": 41.9, "lon": 12.5},    # map centering
                    zoom=4.8,                               # map zooming
                    opacity=0.5,                            # color opacity
                    title='Zone colore dell\'Italia',
                    mapbox_style="carto-positron",
                    height=600,                    
        )

        fig.update_geos(showcountries=False, showcoastlines=False, showland=False, fitbounds="locations")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig.update_layout(legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99
        ))

        st.plotly_chart(fig)
        