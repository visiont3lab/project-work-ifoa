import streamlit as st
from classificatore import classificatore_venta
import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
def page():
    st.title("Modello predittivo per il colore delle regioni")
    # Importare il dataset
    
    df_iniziale = pd.read_csv("data\ita_regioni_zone_correct.csv")

    #df_iniziale.keys()
    st.markdown('''
        Prendendo in input il database regionale sulla situazione del Covid-19 in Italia fornito dalla Protezione Civile, si allena un modello di Machine Learning che è in grado di predire il colore di una regione partendo da dati di input arbitrari.
        
        È possibile inserire una nuova feature combinandone due già esistenti come, ad esempio, il rapporto tra i casi da sospetto diagnostico ed il numero di nuovi positivi.


    ''')


    # Scelta delle features del db della protezione civile da usare
    first_chosen_inputs=["ricoverati_con_sintomi","terapia_intensiva",
            "totale_ospedalizzati","totale_positivi","isolamento_domiciliare",
            "deceduti","dimessi_guariti","nuovi_positivi",
            'variazione_totale_positivi',"totale_casi","tamponi",
            'totale_positivi_test_molecolare','totale_positivi_test_antigenico_rapido',
            'tamponi_test_molecolare','tamponi_test_antigenico_rapido','casi_da_screening','casi_da_sospetto_diagnostico','zona']

    df_with_first_chosen_inputs=df_iniziale[first_chosen_inputs].copy()

    #df_with_first_chosen_inputs.dtypes

    #print(df_with_first_chosen_inputs.tail())

    # Parte di scelta delle features da combinare
    # nella scelta non ci potrà essere 'zona'!!!!

    #st.write('Queste sono le features scelte da cui partire per poter fare una classificazione:\n')
    lista_scelte_possibili=first_chosen_inputs
    lista_scelte_possibili.remove('zona')
    lista_scelte_possibili.sort()

    #for i in lista_scelte_possibili :
    #st.markdown(lista_scelte_possibili)
        #k+=1
        #st.write('\n')

    st.write('Possiamo a costruire una nuova feature per il nostro modello. Dovrai scegliere due feature dall\' elenco di quelle possibili \
        e due potenze con le quali elevare i dati in esse presenti. \n')
    st.write('\n')
    prima_scelta=st.selectbox(label= 'Scegli la prima feature:', options=lista_scelte_possibili)
    st.write('\n')
    lista_scelte_possibili_da_tagliare=lista_scelte_possibili

    lista_scelte_possibili_da_tagliare.remove(prima_scelta)

    #lista_scelte_possibili_da_tagliare.sort()

    seconda_scelta=st.selectbox(label= 'Scegli la seconda feature:', options=lista_scelte_possibili_da_tagliare)
    st.write('\n')
    chosen_feature_1 = prima_scelta # deve diventare una scelta da bottone
    chosen_feature_2 = seconda_scelta # deve diventare una scelta da bottone


    # Alerts che avvisano della presenza di NaN nelle features da combinare scelte
    #alert_1 = df_with_first_chosen_inputs[chosen_feature_1].isnull().sum()
    #alert_2 = df_with_first_chosen_inputs[chosen_feature_2].isnull().sum()
    #if alert_1 !=0 :
    #    print('Attenzione! La prima feature scelta contiene '+ str(alert_1) + ' valori "NaN"')
    #elif alert_2 !=0 :
    #    print('Attenzione! La seconda feature scelta contiene '+ str(alert_2) + ' valori "NaN"')

    stringa_scelta_1='Scegli a quale potenza elevare i dati di \"'+chosen_feature_1+'\"'
    stringa_scelta_2='Scegli a quale potenza elevare i dati di \"'+chosen_feature_2+'\"'
    powers_list=[-2,-1,1,2]
    # Scelta delle potenze alle quali elevare i valori delle features
    power_for_chosen_feature_1 = st.radio(label=stringa_scelta_1, options=powers_list, index=2) #TODO deve diventare una scelta da bottone
    st.write('\n')

    power_for_chosen_feature_2 = st.radio(label=stringa_scelta_2, options=powers_list, index=1) #TODO deve diventare una scelta da bottone
    #power_for_chosen_feature_2 = -1 #TODO deve diventare una scelta da bottone

    st.write('\n')
    st.write('\n')

    #st.markdown('''
    #    Cliccando il seguente bottone sarà visualizzata la confusion matrix per il modello ed un grafico con la feature importance dei dati utilizzati per effettuare la classificazione.
    #''')
    interruttore=st.button(label='Avvia il modello di classificazione')
    if interruttore:
        classificatore_venta(chosen_feature_1, chosen_feature_2, power_for_chosen_feature_1, power_for_chosen_feature_2,df_with_first_chosen_inputs)