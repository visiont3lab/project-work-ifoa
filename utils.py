import cv2
import numpy as np
import base64
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time, timedelta, date

# pip install streamlit --upgrade
# pip install streamlit==0.78.0

def fig_stats(regione, data_inizio, data_fine):
    select = ["deceduti","totale_casi","dimessi_guariti","variazione_totale_positivi"]
    df = None
    if regione=="Italia":
        df = get_data_nazione()
    else:
        df = get_data_regioni()
        df = df[df["denominazione_regione"]==regione]

    #df = df[ (df["data"]>=data_inizio) & (df["data"]<=data_fine) ]
    fig = go.Figure()
    for name in select:
        fig.add_trace(go.Scatter(x=df["data"], y=df[name],
                      mode='lines',#mode='lines+markers',
                      name=name.replace("_"," "),
                      hoverlabel_namelength=-1))
    fig.update_layout(
        showlegend=True,
        hovermode = "x",
        #paper_bgcolor = "rgb(0,0,0)" ,
        #plot_bgcolor = "rgb(10,10,10)" , 
        legend=dict(orientation="h",yanchor="bottom", y=1.02,xanchor="right", x=1,title_text=""),
        dragmode="pan",
        title=dict(
            x = 0.5,
            #text = title,
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

#get_data_locally()