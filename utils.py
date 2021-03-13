import cv2
import numpy as np
import base64
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time, timedelta, date
import wget
from zipfile import ZipFile
import os
import json
import plotly.express as px

# pip install streamlit --upgrade
# pip install streamlit==0.78.0

def fig_stats_variation(regione, data_inizio, data_fine,options):
    #select = ["deceduti","totale_casi","dimessi_guariti","terapia_intensiva","tamponi","isolamento_domiciliare"]
    df = None
    title = "Variazione Giornaliera"
    if regione=="Italia":
        df = get_data_nazione()
        df = df[ (df["data"]>=data_inizio) & (df["data"]<=data_fine) ]  
    else:
        df = get_data_regioni()
        df = df[ (df["data"]>=data_inizio) & (df["data"]<=data_fine) ]
        df = df[df["denominazione_regione"]==regione]
    
    # Script to aggregate data 
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
    dft = df.copy()
    dft = dft.set_index("data")
    dft["count"] = [1 for i in range(0,len(df))]
    agg = {"count" : "size"}
    for s in options:
        agg[s] = "median"
    dft = dft.resample('1D').agg(agg)

    # Variation daily
    df = {"data": dft.index[1:]}
    for s in options:
        start = dft[s][:-1].values
        end = dft[s][1:].values
        df[s] = ( end - start ) 
        #df[s] =  np.round( ( end / start -1 )*100,2)
        
    df = pd.DataFrame(df)
    df = df.set_index("data")
    #dft.dropna()
    #print(dft.head())
    # Rolling average variation


    #df = df[ (df["data"]>=data_inizio) & (df["data"]<=data_fine) ]
    fig = go.Figure()
    for name in options:
        fig.add_trace(go.Scatter(x=df.index, y=df[name],
                      mode='lines+markers',#mode='lines+markers',
                      name=name.replace("_"," "),
                      hoverlabel_namelength=-1))
    fig.update_layout(
        showlegend=True,
        hovermode = "x",
        yaxis_title = "Persone",
        #paper_bgcolor = "rgb(0,0,0)" ,
        #plot_bgcolor = "rgb(10,10,10)" , 
        legend=dict(orientation="h",yanchor="bottom", y=1.02,xanchor="right", x=1,title_text=""),
        dragmode="pan",
        title=dict(
            x = 0.5,
            y = 0.05,
            text = title,
            font=dict(
                size = 20,
                color = "rgb(0,0,0)"
            )
        )
    )
    return fig

def fig_stats(regione, data_inizio, data_fine,options):
    #select = ["deceduti","totale_casi","dimessi_guariti","terapia_intensiva","tamponi","isolamento_domiciliare"]
    df = None
    title = "Andamento Cumulativo"
    if regione=="Italia":

        df = get_data_nazione()
        df = df[ (df["data"]>=data_inizio) & (df["data"]<=data_fine) ]  
        df = df.set_index("data")
    
    else:
        df = get_data_regioni()
        df = df[ (df["data"]>=data_inizio) & (df["data"]<=data_fine) ]
        df = df[df["denominazione_regione"]==regione]
        df = df.set_index("data")
    

    #df = df[ (df["data"]>=data_inizio) & (df["data"]<=data_fine) ]
    fig = go.Figure()
    for name in options:
        fig.add_trace(go.Scatter(x=df.index, y=df[name],
                      mode='lines+markers',#mode='lines+markers',
                      name=name.replace("_"," "),
                      hoverlabel_namelength=-1))
    fig.update_layout(
        showlegend=True,
        hovermode = "x",
        yaxis_title = "Persone",
        #paper_bgcolor = "rgb(0,0,0)" ,
        #plot_bgcolor = "rgb(10,10,10)" , 
        legend=dict(orientation="h",yanchor="bottom", y=1.02,xanchor="right", x=1,title_text=""),
        dragmode="pan",
        title=dict(
            x = 0.5,
            y = 0.05,
            text = title,
            font=dict(
                size = 20,
                color = "rgb(0,0,0)"
            )
        )
    )
    return fig

def get_stats(regione,data_inizio, data_fine):
    select = ["deceduti","totale_casi","dimessi_guariti","variazione_totale_positivi"]
    df = None
    if regione=="Italia":
        df = get_data_nazione()
    else:
        df = get_data_regioni()
        df = df[df["denominazione_regione"]==regione]

    df = df[ (df["data"]>=data_inizio) & (df["data"]<=data_fine) ]
    incremento = ( df.iloc[-1,:][select] - df.iloc[-2,:][select] ) .to_dict()
    data = ( df.iloc[-1,:][select]) .to_dict()
    
    df = pd.DataFrame ([data,incremento],columns=select, index=["Situazione","Incremento"])
    df = df.rename(columns={"deceduti": "Deceduti", "totale_casi": "Totale Casi", "dimessi_guariti": "Dimessi Guariti","variazione_totale_positivi" : "Var. Totale Positivi" })

    return df

def get_nomi_regioni():
    df = get_data_regioni()
    #df["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in  df["data"]]
    return df["denominazione_regione"].unique().tolist()

def get_options():
    select = ["deceduti","totale_casi","dimessi_guariti","terapia_intensiva","tamponi","isolamento_domiciliare"]
    return select

def get_date():
    df = get_data_nazione()
    start =  df["data"].tolist()[0]
    end= df["data"].tolist()[-1]
    d = end
    date = []
    date.append(d.strftime("%Y-%m-%d"))
    while (d>start):
        t = d -timedelta(days=0, weeks=1)
        date.append(t.strftime("%Y-%m-%d"))
        d = t
    #date = [ d.strftime("%Y-%m-%d") for d in  df["data"].dt.date]
    return date

def get_data_nazione():
    '''
    Keys: ['data', 'stato', 'ricoverati_con_sintomi', 'terapia_intensiva',
       'totale_ospedalizzati', 'isolamento_domiciliare', 'totale_positivi',
       'variazione_totale_positivi', 'nuovi_positivi', 'dimessi_guariti',
       'deceduti', 'casi_da_sospetto_diagnostico', 'casi_da_screening',
       'totale_casi', 'tamponi', 'casi_testati', 'note',
       'ingressi_terapia_intensiva', 'note_test', 'note_casi',
       'totale_positivi_test_molecolare',
       'totale_positivi_test_antigenico_rapido', 'tamponi_test_molecolare',
       'tamponi_test_antigenico_rapido']
    '''
    #url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"
    url = "data/dpc-covid19-ita-andamento-nazionale.csv"
    df = pd.read_csv(url)
    df["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in  df["data"]]
    return df

def get_data_province():
    '''
    Keys: ['data', 'stato', 'codice_regione', 'denominazione_regione',
       'codice_provincia', 'denominazione_provincia', 'sigla_provincia', 'lat',
       'long', 'totale_casi', 'note', 'codice_nuts_1', 'codice_nuts_2',        
       'codice_nuts_3']
    '''
    #url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv"
    url = "data/dpc-covid19-ita-province.csv"
    df = pd.read_csv(url)
    df["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in  df["data"]]
    return df

def get_data_regioni():
    '''
    Keys: ['data', 'stato', 'codice_regione', 'denominazione_regione', 'lat',  
       'long', 'ricoverati_con_sintomi', 'terapia_intensiva',
       'totale_ospedalizzati', 'isolamento_domiciliare', 'totale_positivi',
       'variazione_totale_positivi', 'nuovi_positivi', 'dimessi_guariti',  
       'deceduti', 'casi_da_sospetto_diagnostico', 'casi_da_screening',    
       'totale_casi', 'tamponi', 'casi_testati', 'note',
       'ingressi_terapia_intensiva', 'note_test', 'note_casi',
       'totale_positivi_test_molecolare',
       'totale_positivi_test_antigenico_rapido', 'tamponi_test_molecolare',
       'tamponi_test_antigenico_rapido', 'codice_nuts_1', 'codice_nuts_2']
    '''
    #url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
    url = "data/dpc-covid19-ita-regioni.csv"
    df = pd.read_csv(url)
    df["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in  df["data"]]
    return df

def create_dataset(df_p):
    # Data string to datetime
    # Le date sono codificate come stringhe. Le vogliamo come datetime
    df["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in  df["data"]]

    # Filtro emilia - romagna
    df = df[df["denomiazione_regione"]=="Emilia-Romagna"]

    # Dataset (ultime 4 settimane)
    data_end = df["data"].tolist()[-1] # data di oggi
    data_start  = data_end - timedelta(days=0,weeks=2,hours=0,minutes=0) 
    df_f = df[ (df["data"]>=data_start) & (df["data"]<=data_end) ]

    # Dataset (ultime 2 settimane)
    data_end = df["data"].tolist()[-1] # data di oggi
    data_start  = data_end - timedelta(days=0,weeks=1,hours=0,minutes=0) 
    df_ff = df[ (df["data"]>=data_start) & (df["data"]<=data_end) ]

    # Calcolo Indici Regionali Emilia Romagna
    # id1 Totale casi ultime 2 settimate
    i1 = df_f["totale_casi"] 
    #id2 Ricoverati con sentomi utlime 2 settimane
    i2 = df_f["ricoverati_con_sintomi"] 
    #id3 Terapia intensiva ultime 2 settimate
    i3 = df_f["terapia_intensiva"] 
    #id4 Isolamento dociciliare
    i4 = df_f["isolamento_domiciliare"]
    # id7 % tamponi positivi
    i7 = ( df_f["totale_positivi_test_molecolare"] + df_f["totale_positivi_test_antigenico_rapido"] ) /  df_f["tamponi"]  
    # Numero di deceduti nelle 2 settimane
    e1 = df_f["deceduti"] 


    i12 = df_f["casi_da_sospetto_diagnostico"]
    i13 = df_ff["totale_casi"]

def get_data_locally():
    url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv"
    df = pd.read_csv(url)
    df.to_csv("data/dpc-covid19-ita-province.csv")

    url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
    df = pd.read_csv(url)
    df.to_csv("data/dpc-covid19-ita-regioni.csv")

    url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"
    df = pd.read_csv(url)
    df.to_csv("data/dpc-covid19-ita-andamento-nazionale.csv")


def get_map():
    df = pd.read_csv("data/dpc-covid19-ita-regioni-zone.csv")
    df["data"] = [ datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in  df["data"]]
    update_date = df["data"].tolist()[-1]
    df = df[df["data"].dt.date==update_date]
    regions = df["denominazione_regione"].tolist()
    colors = df["zona"].tolist()
    # https://codicicolori.com/codici-colori-rgb
    color_discrete_map = {'unknown':  'rgb(125,125,0)', 'bianca': 'rgb(255,255,255)', 'gialla': 'rgb(255,255,108)', 'arancione': 'rgb(255,165,0)','rossa': 'rgb(255,0,0)'}
    df = pd.DataFrame(regions, columns=['Regione'])
    df['zona'] =colors
    with open('data/regioni.geojson') as f:
        italy_regions_geo = json.load(f)
        # Choropleth representing the length of region names
        fig = px.choropleth(data_frame=df, 
                            geojson=italy_regions_geo, 
                            locations='Regione', # name of dataframe column
                            featureidkey='properties.NOME_REG',  # path to field in GeoJSON feature object with which to match the values passed in to locations
                            color="zona",
                            color_discrete_map=color_discrete_map,
                            scope="europe",
                        )
        fig.update_geos(showcountries=False, showcoastlines=False, showland=False, fitbounds="locations")
        title = "Situazione Italiana: " + update_date.strftime("%Y-%m-%d" )
        fig.update_layout(title=title) #),margin={"r":0,"t":0,"l":0,"b":0})
        return fig

def get_zone_table(regione):
    #df = pd.read_csv("data/dpc-covid-19-aree.csv")
    df = pd.read_csv("data/dpc-covid19-ita-regioni-zone.csv")
    df["data"] = [ datetime.strptime(d, "%Y-%m-%d %H:%M:%S").date() for d in  df["data"]]
    df = df.sort_values(by=["data"],ascending=False)
    if regione!="Italia":
        df = df[df["denominazione_regione"]==regione]
    inputs = ["data","denominazione_regione","zona"] #"ricoverati_con_sintomi","terapia_intensiva","totale_ospedalizzati","totale_positivi","isolamento_domiciliare","deceduti","dimessi_guariti","tamponi","zona"]
    df = df[inputs]
    return df

def collect_data():

    url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"
    df = pd.read_csv(url)
    df.to_csv("data/dpc-covid19-ita-andamento-nazionale.csv")

    url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
    df = pd.read_csv(url)
    df.to_csv("data/dpc-covid19-ita-regioni.csv")

    url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv"
    df = pd.read_csv(url)
    df.to_csv("data/dpc-covid19-ita-province.csv")

    '''
    # bash
    wget https://github.com/pcm-dpc/COVID-19/raw/master/aree/geojson/dpc-covid-19-aree-nuove-g-json.zip
    unzip dpc-covid-19-aree-nuove-g-json.zip
    '''
    url = 'https://github.com/pcm-dpc/COVID-19/raw/master/aree/geojson/dpc-covid-19-aree-nuove-g-json.zip'
    filenameZip = wget.download(url,out="data/dpc-covid-19-aree-nuove-g-json.zip")
    with ZipFile(filenameZip, 'r') as zipObj:
        zipObj.extractall("data/")
        print('File is unzipped') 
        zipObj.close()
    os.remove(filenameZip)

    # Process json file to retrieve data
    with open('data/dpc-covid-19-aree-nuove-g.json') as f:
        data = json.load(f)
        data_dict = {
            "regione" : [],
            "data_inizio": [],
            "data_fine": [],
            "colore" : [],
            "link": []
        }
        color_dict = {"art.1": "gialla","art.2": "arancione","art.3": "rossa", "art.1 comma 11" : "bianca" }
        lista_regioni = []
        for d in data["features"]:
            p = d["properties"]
            data_inizio = datetime.strptime(p["datasetIni"], "%d/%m/%Y")

            if p["datasetFin"]==" ":
                data_fine = datetime.now() #.date()
            else:
                data_fine = datetime.strptime(p["datasetFin"], "%d/%m/%Y") #.date()
            
            regione = p["nomeTesto"]
            colore = color_dict[ p["legSpecRif"] ]

            #if (data_inizio not in data_dict["data_inizio"]):
            data_dict["regione"].append(regione)
            data_dict["data_inizio"].append(data_inizio)
            data_dict["data_fine"].append(data_fine)
            data_dict["colore"].append(colore)
            data_dict["link"].append(p["legLink"])

        df = pd.DataFrame(data_dict)
        df.to_csv("data/dpc-covid-19-aree.csv")

        # Update dataset Regioni
        df_r = pd.read_csv("data/dpc-covid19-ita-regioni.csv")
        df_r["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in  df_r["data"]]
        colors = []
        data_inizio_zone = datetime(2020,11,6)
        # Introdotto da novembre concettto di zona
        for index, row in df_r.iterrows():
            #print(data,regione)
            if row["data"]>=data_inizio_zone:
                dff = df[df["regione"]==row["denominazione_regione"]]
                #print(row["data"])
                dff = dff[ (  (row["data"]>=dff["data_inizio"]) & (row["data"] <=dff["data_fine"] ) )]
                if dff.empty:
                    colors.append("bianca")
                else:
                    colors.append(dff["colore"].tolist()[0])
            else:
                colors.append("unknown")

        df_r["zona"] = colors   
        df_r.to_csv("data/dpc-covid19-ita-regioni-zone.csv")
        
