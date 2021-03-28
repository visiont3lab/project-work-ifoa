import streamlit as st
import utils

# Informazioni Utili
# pip install streamlit --upgrade
# Run: streamlit run app.py

@st.cache
def get_data():
    # Esegue la funzione solo la priva volta che viene vista
    df_n = utils.get_data_nazione()
    df_r = utils.get_data_regioni()
    df_p = utils.get_data_province()
    return df_n,df_r, df_p

# Title
st.title("Analisi Covid 2020-2021")

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
col1, col2, col3 = st.beta_columns(3)
with col1:
    data_inizio = st.selectbox("Data Inzio", date[1:])
with col2:
    data_fine = st.selectbox("Data Fine", date)
with col3:
    nomi_regioni = utils.get_nomi_regioni() 
    nomi_regioni.insert(0,"Italia") 
    regione = st.selectbox("Analisi", nomi_regioni)
st.table(utils.get_stats(regione,data_inizio,data_fine)) # try also st.write(), st.dataframe
fig = utils.fig_stats(regione,data_inizio,data_fine)
st.plotly_chart(fig, use_container_width=True)
st.markdown('''

TODO:

* [Federico Valisi] Creare un grafico che mostra la variazione dei deceduti, totale casi,
dimessi guariti, variazione totale positivi nel range di date scelto. Rispondiamo 
alla domanda da ..  a .. quanti deceduti ci sono?

''')
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# Situazione Colori Regioni
# https://github.com/pcm-dpc/COVID-19/issues/1045
st.markdown('''## Situazione Zone di Rischio (Colori ) Regionale ''')

st.markdown('''

TODO:

* [Federico Venta] Creare script automatico di aggiornameto colore regioni. Serve a  raccogliere i dati del colore delle regioni.
* [Tiziana] Visualizzare attraverso una mappa il cambiamento di colore delle diverse regioni italiane. Oppure sempre usanda da .. a .. 
in base alla data visualizzare la mappa delle regione colorata a zone.

Il colore delle regione ad oggi è visibile a nel sito del ministero della satute [Classificazione Regioni e Province autonome
aggiornamento all'8 marzo](http://www.salute.gov.it/portale/nuovocoronavirus/dettaglioContenutiNuovoCoronavirus.jsp?area=nuovoCoronavirus&id=5351&lingua=italiano&menu=vuoto)
''')
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# Definizione degli input
st.markdown('''## Definizione degli input per stimare le zone di rischio ''')

st.markdown('''

TODO:

* [Leonardo] Definire gli input che saranno utilizzati per il classificatore bassandosi sul dataset regioni.
* [Serena] Definire l'indice Rt.
''')
# --------------------------------------------------------------------


# --------------------------------------------------------------------
# Testare/allenare il modello
st.markdown('''## Definizione degli input per stimare le zone di rischio ''')

st.markdown('''

TODO:

* Creare un form  dove verrano inseriti i gli inputs necessari al modello.
* Allenare e Testare il classificatore.
''')
# --------------------------------------------------------------------


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