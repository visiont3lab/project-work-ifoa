import streamlit as st
import utils

# Page Style
#st.markdown("""
#    <style>
#    body {
#        background: black;
#        color: white; 
#    }
#    </style>
#    """, unsafe_allow_html=True)

# Informazioni Utili
# pip install streamlit --upgrade
# Run: streamlit run app.py

@st.cache
def get_data():
    # Esegue la funzione solo la priva volta che viene vista
    utils.collect_data()

# Title
st.title("Analisi Covid 2020-2021")
# Collect data
update = st.button("Aggiorna i dati")
if update:
    get_data()

st.markdown('''
                * [Github Repository](https://github.com/visiont3lab/project-work-ifoa) 
                * Estrazione colore Zone Italia: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/visiont3lab/project-work-ifoa/blob/main/colab/AnalisiCovidRegioni.ipynb)
                * Classificatore Zone Italia: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/visiont3lab/project-work-ifoa/blob/main/colab/ClassifierZone.ipynb)
            ''')


# Descrizione Applicazione
description='''
## Descrizione

A un anno dall'inizio del lockdown in italia sono stati raccolti numerosi dati relativi
alla pandemia. In particolare la protezione civile ha creato un [dataset](https://github.com/pcm-dpc/COVID-19)
che giornalmente ci fornisce informazioni sull'andamento del Covid-19 a livello provinciale,regionale e nazionale.
L'obbiettivo di questo progetto e di utilizzare questi dati per creare un modello capace di predirre il colore
di rischio associato a una regione ( bianco, giallo, arancione, arancione scuro, rosso). 

Per poter realizzare il modello (classificatore) sarà necessario:

1. Creare un dataset utilizzando i dati [regionali](https://github.com/pcm-dpc/COVID-19/tree/master/dati-regioni). 
Questi contengono informazioni relative a numero  di deceduti, ricoverati e tamponi. Vogliamo utilizzare queste informazioni poichè osservando
i [21 Indicatori forniti dal Ministero della Salute](http://www.salute.gov.it/imgs/C_17_notizie_5152_1_file.pdf)
tali informaziono sono utilizzati per definire il colore della regione.

2. Ottenere le informazioni associate al colore delle regioni nel tempo. Come è cambiato il colore delle regioni nel tempo. 
Poichè affrontiamo un problema di supervised learning  è necessario allenare il nostro classificatore partendo da un set di input-ouput data.
Andremo pertanto a visualizzare e collezionare i dati relativi al colore delle regioni italiane utilizzando i dati delle [aree nuove](https://github.com/pcm-dpc/COVID-19/tree/master/aree/geojson) forniti
sempre dalla protezione civile.

3. Una volta creato il dataset contenente input-output data andremo ad alleare un classicatore capace di stimare
il colore della regione.

Per riassumere al fine di completare il progetto sarà necesario:

1. Creare gli input
2. Creare gli output
3. Creare il modello

'''
st.markdown(description)

# --------------------------------------------------------------------
# Situazione italiana ad oggi italiana
st.markdown('## Situazione Italiana')
date = utils.get_date()
col1, col2, col3= st.beta_columns(3)
with col1:
    data_inizio = st.selectbox("Data Inzio", date[1:])
with col2:
    data_fine = st.selectbox("Data Fine", date)
with col3:
    nomi_regioni = utils.get_nomi_regioni() 
    nomi_regioni.insert(0,"Italia") 
    regione = st.selectbox("Analisi", nomi_regioni)
st.table(utils.get_stats(regione,data_inizio,data_fine)) # try also st.write(), st.dataframe
options = st.multiselect("Seleziona", utils.get_options(),default=utils.get_options())
fig_stats = utils.fig_stats(regione,data_inizio,data_fine,options)
fig_stats_variation = utils.fig_stats_variation(regione,data_inizio,data_fine,options)

st.plotly_chart(fig_stats, use_container_width=True)
st.plotly_chart(fig_stats_variation, use_container_width=True)

st.markdown('''

Obbiettivo:

* Visualizzare l'andamento nel tempo del numero di deceduti,totale_casi,dimessi_guariti,terapia_intensiva,tamponi,isolamento_domiciliare
* Visualizzare la variazione giornaliera dei deceduti,totale_casi,dimessi_guariti,terapia_intensiva,tamponi,isolamento_domiciliare
* Aggiungere la possibiltà di filtrare per data e di selezionare solo quello che si desidera visualizzare.

''')
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# Situazione Colori Regioni
# https://github.com/pcm-dpc/COVID-19/issues/1045
st.markdown('''
    ## Situazione Zone di Rischio (Colori ) Regionale 

    * [Dowload Dataset](https://github.com/visiont3lab/project-work-ifoa/blob/main/data/dpc-covid19-ita-regioni-zone.csv)
    
    Il dataset è stato ottenuto utilizzando il notebook [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]
    (https://colab.research.google.com/github/visiont3lab/project-work-ifoa/blob/main/colab/AnalisiCovidRegioni.ipynb) 
    e partendo dai dati delle [aree della protezione civile](https://github.com/pcm-dpc/COVID-19/tree/master/aree)
               
''')


regione = st.selectbox("Seleziona la Regione", nomi_regioni)
st.dataframe(utils.get_zone_table(regione))
map_btn = st.button("Visualizza Mappa") 
if map_btn:
    map_zone  = utils.get_map()
    st.plotly_chart(map_zone)

st.markdown('''

Obbiettivo:

* Raccogliere, in modo automatico, i dati corrispondenti al colore delle regioni.
* Visualizzare attraverso una mappa il cambiamento di colore delle diverse regioni italiane in data specifica.

Il colore delle regione ad oggi è visibile a nel sito del ministero della satute [Classificazione Regioni e Province autonome
aggiornamento all'8 marzo](http://www.salute.gov.it/portale/nuovocoronavirus/dettaglioContenutiNuovoCoronavirus.jsp?area=nuovoCoronavirus&id=5351&lingua=italiano&menu=vuoto)
''')
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# Modello
st.markdown('''
    ## Modello per predire il colore di una regione 
    Il classifcatore di colore (pericolosità) della regione è stato sviluppato nel seguente notebook

    * Classificatore Zone Italia: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/visiont3lab/project-work-ifoa/blob/main/colab/ClassifierZone.ipynb)

    Di seguito forniamo un form capace, fornendo gli inputs indicati, di predirre la zona di rischio (bianca, arancione, gialla, rossa) di una regione.         

    Note:
    * Sarebbe interessante aggiungere l'indice Rt come input  del classificatore.
    ''')
nomi_regioni = utils.get_nomi_regioni() 
regione = st.selectbox("Nome Regione", nomi_regioni, index=4)

ricoverati_con_sintomi,terapia_intensiva,totale_ospedalizzati,totale_positivi,isolamento_domiciliare,deceduti,dimessi_guariti,nuovi_positivi,totale_casi,tamponi = utils.get_input_prediction(regione)
col1, col2, col3, col4, col5 = st.beta_columns(5)
with col1:
    tamponi = st.text_input("tamponi",value=tamponi)
with col2:
    deceduti = st.text_input("Deceduti",value=deceduti)
with col3:
    totale_casi = st.text_input("Totale Casi",value=totale_casi)
with col4:
    dimessi_guariti = st.text_input("Dimessi Guariti",value=dimessi_guariti)
with col5:
    totale_ospedalizzati = st.text_input("Totale Ospedalizzati",value=totale_ospedalizzati)
col1, col2, col3, col4, col5 = st.beta_columns(5)
with col1:
    ricoverati_con_sintomi = st.text_input("Ricoverati Con Sintomi",value=ricoverati_con_sintomi)
with col2:
    totale_positivi = st.text_input("Totale Positivi",value=totale_positivi)
with col3:
    isolamento_domiciliare = st.text_input("Isol. Domiciliare",value=isolamento_domiciliare)
with col4:
    terapia_intensiva = st.text_input("Terapia Intensiva",value=terapia_intensiva)
with col5:
    nuovi_positivi = st.text_input("Nuovi Positivi",value=nuovi_positivi)
# --------------------------------------------------------------------

inf = utils.Inference()
pred = inf.predict([ricoverati_con_sintomi,terapia_intensiva,totale_ospedalizzati,totale_positivi,isolamento_domiciliare,deceduti,dimessi_guariti,nuovi_positivi,totale_casi,tamponi],regione)
st.write("Predizione Colore Zona: " + regione + " --> "+pred)

# --------- Material Extra
st.markdown('''
## Link Utili

* [Dati covid italia](https://dati-covid.italia.it/)
* [Protezione Civilie Covid-19 Open data](https://github.com/pcm-dpc/COVID-19)
* [21 Indicatori Covid Ministero della Salute](http://www.salute.gov.it/imgs/C_17_notizie_5152_1_file.pdf)
* [Dataset regioni colore](https://github.com/imcatta/restrizioni_regionali_covid)
* [Streamlit Api](https://docs.streamlit.io/en/stable/api.html)
* [Visualizzare la diffussione del covid](https://medium.com/polimi-data-scientists/how-to-visualize-the-spread-of-covid-19-in-italy-6d9ddea18a02)
* [Come leggere i dati aree (Issue)](https://github.com/pcm-dpc/COVID-19/issues/1045)
''')