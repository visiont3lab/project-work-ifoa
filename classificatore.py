def classificatore_venta(number_of_estimators,chosen_feature_1, chosen_feature_2, power_for_chosen_feature_1, power_for_chosen_feature_2,df_with_first_chosen_inputs):
    import streamlit as st
    import pandas as pd
    from datetime import datetime
    import numpy as np
    ###############################################################
    # Codice per assegnare il nome corretto alla nuova colonna
    # da visualizzare poi nelle immagini
    ###############################################################
    if ((power_for_chosen_feature_1 == 1) and (power_for_chosen_feature_2 == -1)):
        new_feature_name = chosen_feature_1 + '/' + chosen_feature_2

    elif ((power_for_chosen_feature_1 == -1) and (power_for_chosen_feature_2 == 1)):
        new_feature_name = chosen_feature_2 + '/' + chosen_feature_1

    elif ((power_for_chosen_feature_1 == 1) and (power_for_chosen_feature_2 == 1)):
        new_feature_name = chosen_feature_1 + ' * ' + chosen_feature_2

    else :
        power_1_converted_to_string = "% s" % power_for_chosen_feature_1
        power_2_converted_to_string = "% s" % power_for_chosen_feature_2    
        new_feature_name = chosen_feature_1 + '^(' + power_1_converted_to_string \
        + ') * ' + chosen_feature_2 + '^(' + power_2_converted_to_string +')'
    ###############################################################
    # End: Codice per assegnare il nome corretto alla nuova colonna
    ###############################################################

    # Creazione della nuova feature derivata, viene automaticamente aggiunta
    # al DataFrame
    df_with_first_chosen_inputs[new_feature_name] = \
    df_with_first_chosen_inputs[chosen_feature_1].astype(float).pow(power_for_chosen_feature_1)* \
    df_with_first_chosen_inputs[chosen_feature_2].astype(float).pow(power_for_chosen_feature_2)

    # Elimino i NaN rimpiazzandoli con la media della colonna
    df_with_first_chosen_inputs.fillna(df_with_first_chosen_inputs.mean(), inplace=True)

    # Rinomino il dataframe sul quale andrò a fare classificazione
    df=df_with_first_chosen_inputs.copy()

    # Ottengo la lista degli input, togliendo la colonna "zona" che sarà la nostra target
    lista_keys_df = list(df.keys())
    lista_keys_df.remove('zona')
    inputs=lista_keys_df

    # Definizione delle features
    df_X = df[inputs].copy()

    # Parte da utilizzare qualora si vogliano settare dummy variables per le regioni
    # oneHot = pd.get_dummies(df["denominazione_regione"], prefix='R')
    # for k in oneHot.keys():
    #     df_X[k] = oneHot[k]

    # Definizione della target
    df_Y = df["zona"]

    # Definizione Classi
    dict_names = {"bianca":0,"gialla": 1, "arancione": 2, "rossa": 3}
    names = list(dict_names)

    X = df_X.values
    Y = np.array([dict_names[d] for d in df_Y],dtype=np.float)


    # Parte Training
    from sklearn import datasets
    import numpy as np
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import LinearSVC,SVC
    import plotly.graph_objects as go
    from sklearn.metrics import confusion_matrix,classification_report
    from sklearn.model_selection import train_test_split, GridSearchCV,RandomizedSearchCV
    from sklearn.decomposition import PCA
    import joblib
    from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, GradientBoostingClassifier
    st.write('\n')
    st.write('\n')
    st.markdown('''
        Riportiamo la parte di codice corrispondente alla pipeline per il modello di classificazione:

    ''')

    with st.echo():
        # Divisione del campione in train e test
        X_train, X_test, Y_train, Y_test  = train_test_split(X, Y, test_size=0.2, random_state=42)

        pipeline = Pipeline([
            ("sc", StandardScaler()),
            ('model',RandomForestClassifier(n_estimators=number_of_estimators))
        ])

        # Fit
        pipeline.fit(X_train,Y_train)
    
    ############################################################################################################
    ############################################################################################################
    ############################################################################################################
    #
    #  Le seguenti linee di codice erano nella pipeline, subito dopo "("sc", StandardScaler()),"
    #
    # 0-1 features
    #('polinomial', PolynomialFeatures(degree=3)),
    #("pca", PCA(n_components=0.99)),
    #("model", SVC(kernel="rbf",C=10,gamma=1,probability=True) ) # Probability true slow down dataset
    #("model", SVC(kernel="linear",C=1000,gamma=100,probability=True) ) # Probability true slow down dataset
    #('model', GradientBoostingClassifier(learning_rate=0.05,n_estimators=150))
    ############################################################################################################
    ############################################################################################################
    ############################################################################################################

    # Save trained model
    joblib.dump(pipeline, "model.pkl") 

    #print(pipeline)

    # Parte Testing
    import joblib
    import pandas as pd
    import numpy as np
    from sklearn.metrics import confusion_matrix,classification_report

    class Inference:
        def __init__(self,model_path="model.pkl"):
            dict_names = {"bianca":0,"gialla": 1, "arancione": 2, "rossa": 3}
            self.names = list(dict_names)
            self.model = joblib.load(model_path)
        def predict(self,X):
            Y_hat = self.model.predict(X)
            return Y_hat
        def report(self,X,Y):
            Y_hat = self.predict(X)
            names_pred = [ "Pred: " + n for n in self.names]
            #print("Confusion Matrix")
            cm = confusion_matrix(Y,Y_hat)
            df = pd.DataFrame(cm, columns=names_pred, index=names)
            print(df)
            st.dataframe(df)
            #print("Report")
            #print(classification_report(Y, Y_hat))

    #TODO mettere comandi Streamlit
    inf = Inference()
    st.write('\n')
    st.markdown('''
    Si ottiene la confusion matrix per il campione di training:
    ''')
    st.write('\n')
    st.write("\n ------- Training Results\n")
    inf.report(X_train,Y_train)
    st.write('\n')
    st.markdown('''
    Nella fase di test, otteneniamo invece la seguente confusion matrix:
    ''')
    st.write("\n ------- Test Results\n")
    inf.report(X_test,Y_test)
    st.write('\n')
    
    # Score
    score = pipeline.score(X_test,Y_test)
    #st.write(pipeline)
    st.write('\n')
    st.markdown('''
        Si può valutare l'accuracy del modello tramite lo score
    ''')
    st.latex(r'''
        F_{1}=2 \, \cdot \, \frac{\mathrm{precision}\, \cdot \, \mathrm{recall}}{\mathrm{precision}\, + \, \mathrm{recall}}
    ''')
    st.write('\n')
    st.write("Per questa classificazione, F_1 = ", score)

    # Parte di Feature Importance

    import joblib
    import numpy as np
    import plotly.graph_objects as go

    inputs_fin = df_X.keys()

    model = joblib.load("model.pkl")
    model = pipeline.named_steps["model"]
    importances = model.feature_importances_
    std = np.std([tree.feature_importances_ for tree in model.estimators_],axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    #print("Feature ranking:")
    xplot = []
    yplot = []
    for f in range(X.shape[1]):
        xplot.append(inputs_fin[indices[f]])
        yplot.append(np.round(importances[indices[f]],3))
        #print("%s %s (%s)" % (f + 1,inputs[indices[f]] , np.round(importances[indices[f]],3)))

    # Plot the impurity-based feature importances of the forest
    fig = go.Figure()
    fig.add_traces(go.Bar(x=xplot, y=yplot))
    fig.update_layout(title="Input features Importance")
    
    st.plotly_chart(fig, use_container_width=True)
""" 
    #PROVA CLASSIFICATORE MANUALE
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
        #url = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
        url = "data/dpc-covid19-ita-regioni.csv"
        df = pd.read_csv(url)
        df["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S") for d in  df["data"]]
        return df
    def get_input_prediction(regione):
        df = pd.read_csv("data/dpc-covid19-ita-regioni-zone.csv")
        df = df[df["denominazione_regione"]==regione]
        last = df.tail(1)
        ricoverati_con_sintomi = last["ricoverati_con_sintomi"].tolist()[0]
        terapia_intensiva = last["terapia_intensiva"].tolist()[0]
        totale_ospedalizzati = last["totale_ospedalizzati"].tolist()[0]
        totale_positivi = last["totale_positivi"].tolist()[0]
        isolamento_domiciliare = last["isolamento_domiciliare"].tolist()[0]
        deceduti = last["deceduti"].tolist()[0]
        dimessi_guariti = last["dimessi_guariti"].tolist()[0]
        nuovi_positivi = last["nuovi_positivi"].tolist()[0]
        totale_casi = last["totale_casi"].tolist()[0]
        tamponi = last["tamponi"].tolist()[0]
        return ricoverati_con_sintomi,terapia_intensiva,totale_ospedalizzati,totale_positivi,isolamento_domiciliare,deceduti,dimessi_guariti,nuovi_positivi,totale_casi,tamponi    

    nomi_regioni = get_nomi_regioni() 
    regione = st.selectbox("Nome Regione", nomi_regioni, index=4)

    ricoverati_con_sintomi,terapia_intensiva,totale_ospedalizzati,totale_positivi,isolamento_domiciliare,deceduti,dimessi_guariti,nuovi_positivi,totale_casi,tamponi = get_input_prediction(regione)
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

    #inf = Inference()
    pred = inf.predict([ricoverati_con_sintomi,terapia_intensiva,totale_ospedalizzati,totale_positivi,isolamento_domiciliare,deceduti,dimessi_guariti,nuovi_positivi,totale_casi,tamponi],regione)
    st.write("Predizione Colore Zona: " + regione + " --> "+pred)

    import seaborn as sns
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    sns.heatmap(df_col.corr(), ax=ax)
    st.write(fig)
 """