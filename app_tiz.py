import streamlit as st
from urllib.request import urlopen
import json
from datetime import datetime
import pandas as pd
import plotly.express as px

with open('./data/limits_IT_regions.geojson') as confini:
    italy_regions_geo = json.load(confini)
df = pd.read_csv("https://raw.githubusercontent.com/visiont3lab/project-work-ifoa/main/data/zone_regioni_esteso.csv")
date = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f") for d in  df["data_inizio"]]
df["data"] = date
color_discrete_map = {'unknown':  'rgb(1,0,0)', 'bianca': 'white', 'gialla': 'yellow', 'arancione': 'orange','rossa': 'red'}

data_selection = st.date_input('Seleziona una data:')

map_df = df[df["data"]==data_selection]
fig = px.choropleth_mapbox(data_frame=map_df, 
                locations='regione',                    # dataframe column to match with featureidkey
                geojson=italy_regions_geo,              # geojson
                featureidkey='properties.reg_name',     # path of the geojson field to match with locations
                color="zona",
                color_discrete_map=color_discrete_map,  # color map defined above
                center = {"lat": 41.9, "lon": 12.5},    # map centering
                zoom=4.5,                               # map zooming
                opacity=0.5,                            # color opacity
                title='Italian Rt zones',
                mapbox_style="carto-positron",
                height=600,                    
)

fig.update_geos(showcountries=False, showcoastlines=False, showland=False, fitbounds="locations")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig)