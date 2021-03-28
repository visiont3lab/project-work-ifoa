from urllib.request import urlopen
import json
from datetime import datetime
import pandas as pd
import plotly.express as px

with open('limits_IT_regions.geojson') as f:
    italy_regions_geo = json.load(f)
df = pd.read_csv("https://raw.githubusercontent.com/visiont3lab/project-work-ifoa/main/data/zone_regioni_esteso.csv")
date = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f") for d in  df["data_inizio"]]
df["data"] = date
color_discrete_map = {'unknown':  'rgb(1,0,0)', 'bianca': 'white', 'gialla': 'yellow', 'arancione': 'orange','rossa': 'red'}
update_date = datetime(2021,3,22)
t = df[df["data"]==update_date]

fig = px.choropleth_mapbox(data_frame=t, 
                    locations='regione',                    # dataframe column to match with featureidkey
                    geojson=italy_regions_geo,              # geojson
                    featureidkey='properties.reg_name',     # path of the geojson field to match with locations
                    color="zona",
                    color_discrete_map=color_discrete_map,  # color map defined above
                    center = {"lat": 41.9, "lon": 12.5},    # map centering
                    zoom=4,                                 # map zooming
                    opacity=0.5,                            # color opacity
                    title='Italian Rt zones',
                    mapbox_style="carto-positron",
                    height=600,                    
)

fig.update_geos(showcountries=False, showcoastlines=False, showland=False, fitbounds="locations")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()