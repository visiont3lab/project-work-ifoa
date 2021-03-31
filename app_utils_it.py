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
import joblib 

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
    url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv"
    #url = "data/dpc-covid19-ita-andamento-nazionale.csv"
    df = pd.read_csv(url)
    df["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in  df["data"]]
    return df

def get_nomi_regioni():
    df = get_data_regioni()
    #df["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in  df["data"]]
    return df["denominazione_regione"].unique().tolist()    

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
    url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
    #url = "data/dpc-covid19-ita-regioni.csv"
    df = pd.read_csv(url)
    df["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in  df["data"]]
    return df

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

def get_options():
    select = ["deceduti","totale_casi","dimessi_guariti","terapia_intensiva","tamponi","isolamento_domiciliare"]
    return select