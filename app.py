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


st.set_option('deprecation.showfileUploaderEncoding', False)

st.title("Computer Vision App")

st.markdown('''

## Introduzione
> Applicazione di computer vision con focus threshold

## Setup

### Local PC

```pyhton
virtualen env
source env/bin/activate
pip install streamlit opencv-python
```

### Setup Colab

!wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
!unzip ngrok-stable-linux-amd64.zip
get_ipython().system_raw('./ngrok http 8501 &')
!curl -s http://localhost:4040/api/tunnels | python3 -c \
    'import sys, json; print("Execute the next cell and the go to the following URL: " +json.load(sys.stdin)["tunnels"][0]["public_url"])'
!pkill -9 ngrok
''')


st.sidebar.markdown('''
## Demo Algoritmo

1. Carica un immagine [estensione "png","jpeg","jpg","bmp"]
2. Prova a modifcare lo slider per vedere gli effetti della threshold

''')
thresh_par = st.sidebar.slider('Threshold', 1, 255, 127)
option = st.sidebar.radio('Select Threshold type',('THRESH_BINARY', 'THRESH_BINARY_INV', 'THRESH_TOZERO'))
thresh_sel_par = cv2.THRESH_BINARY

if option:
    if option=="THRESH_BINARY":
        thresh_sel_par = cv2.THRESH_BINARY
    elif option=="THRESH_BINARY_INV":
        thresh_sel_par = cv2.THRESH_BINARY_INV
    else:
        thresh_sel_par = cv2.THRESH_TOZERO
 
uploaded_file = st.sidebar.file_uploader("Upload Image", type=["png","jpeg","jpg","bmp"])
if uploaded_file is not None:
    #print(np.fromstring(uploaded_file.read(), np.uint8))
    image = cv2.imdecode(np.fromstring(uploaded_file.read(), np.uint8),cv2.IMREAD_COLOR)

    #base64_img_bytes = uploaded_file.read() # byte
    #decoded_image_data = base64.decodebytes(base64_img_bytes)
    #nparr = np.fromstring(decoded_image_data, np.uint8)
    #img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # cv2.IMREAD_COLOR in OpenCV

    # ----------
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    ret, tresh = cv2.threshold(gray,thresh_par,255,thresh_sel_par)

    #------------

    st.sidebar.image(tresh, use_column_width=True ) # width=700)
    st.sidebar.image(gray, use_column_width=True) # width=700)
    

st.header("Covid Analisi")
df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv")
df["data"] = [el[0:10] for el in df["data"].values.tolist()]
st.dataframe(df, height=300, width=700)

select = ["deceduti","totale_casi","dimessi_guariti"]
select_options = st.multiselect('Seleziona cosa vuoi plottare', list(df.keys()), default=select)

fig = plot_plotly(df,x ="data", y=select_options,title="Andamento Nazionale")    
st.plotly_chart(fig, use_container_width=True)