import streamlit as st
import cv2
import numpy as np
import base64
import pandas as pd
import plotly.graph_objects as go

def plot_plotly(df,x, y,title):
    n = df[x].values.tolist()
    fig = go.Figure()
    for name in y:
        m = df[name]
        fig.add_trace(go.Scatter(x=n, y=m,
                      mode='lines',#mode='lines+markers',
                      name=name))
    fig.update_layout(
        showlegend=False,
        hovermode = "x",
        #paper_bgcolor = "rgb(0,0,0)" ,
        #plot_bgcolor = "rgb(10,10,10)" , 
        dragmode="pan",
        title=dict(
            x = 0.5,
            text = title,
            font=dict(
                size = 20,
                color = "rgb(0,0,0)"
            )
        )
    )
    return fig


st.header("Covid Analisi")

df_nazionale = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv")
#df_regionale = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv")
#df_provinciale = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province.csv")

st.dataframe(df_nazionale.head())  # Same as st.write(df)
#st.dataframe(df_regionale)  # Same as st.write(df)
#st.dataframe(df_provinciale)  # Same as st.write(df)


#select = ["deceduti","totale_casi","dimessi_guariti"]
#select_options = st.multiselect('Seleziona cosa vuoi plottare', list(df.keys()), default=select)
options = st.multiselect(
    'Choose your plot data',
    ['deceduti', 'totale_casi', 'dimessi_guariti'],
    default=["deceduti"])

fig = plot_plotly(df_nazionale,x ="data", y=options,title="Andamento Nazionale")
st.plotly_chart(fig)