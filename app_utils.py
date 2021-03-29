import pandas as pd
import numpy as np
import json
from zipfile import ZipFile
import wget
from datetime import datetime, time, timedelta, date
import plotly.express as px


#ritorna il file json
def get_data():
    url = 'https://github.com/pcm-dpc/COVID-19/raw/master/aree/geojson/dpc-covid-19-aree-nuove-g-json.zip'
    filenameZip = wget.download(url)
    with ZipFile(filenameZip, 'r') as zipObj:
        zipObj.extractall()
    #print('File is unzipped') 
    with open('dpc-covid-19-aree-nuove-g.json') as file:
        data = json.load(file)
    return data

def create_properties_df(data):   
    properties=[]
    for obs in data["features"]:
        properties.append(obs["properties"])
    keys = properties[0].keys()
    d = {}
    for k in keys:
        d[k] = [d[k] for d in properties]
    df = pd.DataFrame(d)
    return df

def drop_and_rename_df(df):
    cols = ['FID', 'localID', 'namespace', 'ID_Evento', 'ID_EventoS',
        'nomeLingua', 'nomeStatus', 'nomeOrigin', 'nomePronun', 'nomeFonte',
            'nomeScript', 'tipoZona', 'tipoZonaSp', 'designIniz',
        'designFine', 'dominioAmb', 'nomeAutRuo', 'legNome', 'legData', 'legDataTip',
        'legLink',  'legNumID', 'legDocUff', 'legDataApp',
        'legDataAbr',  'legGU_ISSN', 'legGU_ISBN',
        'legGU_Link']
    df.drop(columns=cols, inplace=True)
    new_cols = {"nomeTesto" : "regione", "legSpecRif" : "articolo", "legLivello" : "livello"}
    df.rename(columns=new_cols, inplace=True)

def convert_to_datetime(df):      
    data_inizio_list = []
    data_fine_list = []
    for i, row in df.iterrows():
        data_inizio = row["datasetIni"]
        data_inizio = datetime.strptime(data_inizio, "%d/%m/%Y")
        data_fine = row["datasetFin"]
        if data_fine == " ":
            data_fine = datetime.now()
        else:
            data_fine = datetime.strptime(data_fine, "%d/%m/%Y")
        data_inizio_list.append(data_inizio)
        data_fine_list.append(data_fine)
    df["datasetIni"] = data_inizio_list
    df["datasetFin"] = data_fine_list    

def sort_and_rest_index(df):
    df.sort_values(by=["regione", "datasetIni"], inplace=True)
    df.reset_index(inplace=True)

def clean_date(df, col):
    raw_list = df[col].to_list()
    raw_list = [a.split() for a in raw_list]
    date = []
    for el in raw_list:
        date.append(el[1])
    df[col] = [datetime.strptime(d, "%d/%m/%Y") for d in date]

def duplicated_index(df_r, col):        #ritorna gli indici delle righe con duplicato in col
    dupl = df_r[col].duplicated(keep=False)
    check = dupl.sum()
    if check:
        return df_r[dupl].index.to_list()
    else:
       return []

def correct_date_misclass(df_r, idx1, idx2):
    art_a = df_r.loc[idx1,"articolo"]
    art_b = df_r.loc[idx2,"articolo"]
    if art_a > art_b:
        df_r.drop(idx2, inplace=True)
    else:
        df_r.drop(idx1, inplace=True)

def correct_date_downgrading(df_r, idx1, idx2):
    df_r.loc[idx1,"datasetFin"] = df_r.loc[idx2, "legGU_ID"]
    df_r.loc[idx2, "datasetIni"] = df_r.loc[idx2, "legGU_ID"]
    
def correct_date_extension(df_r, idx1, idx2):
    data_fine1 = df_r.loc[idx1, "datasetFin"]
    data_fine2 = df_r.loc[idx2, "datasetFin"]
    if data_fine2 > data_fine1:
        df_r.drop(idx1, inplace=True)
    else:
        df_r.drop(idx2, inplace=True)

def correct_date_restriction(df_r, idx1, idx2):
    data_inizio1 = df_r.loc[idx1, "datasetIni"]
    data_inizio2 = df_r.loc[idx2, "datasetIni"]
    if data_inizio1 < data_inizio2:
        df_r.loc[idx1,"datasetFin"] = data_inizio2 
    else:
        df_r.loc[idx2,"datasetFin"] = data_inizio1

def split_half(l):
    half = len(l)//2
    if half==2:
        a = l[:half]
        b = l[half:]
        return [a,b]
    else:
        return [l]

def get_indexes(df_r):
    index_ini = duplicated_index(df_r, "datasetIni")
    index_fin = duplicated_index(df_r, "datasetFin")
    index_leg = duplicated_index(df_r, "legNomeBre")
    l1 = split_half(index_ini)
    l2 = split_half(index_fin)
    l3 = split_half(index_leg)
    index_misclass = [x for x in l1+l2+l3 if x in l1 and x in l2 and x in l3]   #indici del caso A di misclasificazione
    index_downgrade = [x for x in l1+l2+l3 if x in l1 and x in l2 and x not in l3] #indici del caso B di downgrading
    index_extension = [x for x in l1+l2+l3 if x in l1 and x not in l2 and x not in l3] #indici del caso C di extension
    index_restrict = [x for x in l1+l2+l3 if x not in l1 and x in l2 and x not in l3] # indici del cado D di restringimento
    indexes = [index_misclass, index_downgrade, index_extension, index_restrict]
    index_list = []
    for index in indexes:
        if index!=[]:
            index_list.append(index[0])
        else:
            index_list.append(index)
    index_dict = {
        "misclass" : index_list[0],
        "downgrade" : index_list[1],
        "extension" : index_list[2],
        "restrict" : index_list[3]
    }
    return index_dict

def correct_date_all(df_r):
    if get_indexes(df_r)["misclass"]!=[]:
        idx1, idx2 = get_indexes(df_r)["misclass"]
        correct_date_misclass(df_r, idx1, idx2)

    if get_indexes(df_r)["extension"]!=[]:
        idx1, idx2 = get_indexes(df_r)["extension"]
        correct_date_extension(df_r, idx1, idx2)

    if get_indexes(df_r)["restrict"]!=[]:
        idx1, idx2 = get_indexes(df_r)["restrict"]
        correct_date_restriction(df_r, idx1, idx2)

    if get_indexes(df_r)["downgrade"]!=[]:
        idx1, idx2 = get_indexes(df_r)["downgrade"]
        correct_date_downgrading(df_r, idx1, idx2)

def clean_dataset_first(df): 
    regioni = df["regione"].unique()
    df_clean = pd.DataFrame()
    for regione in regioni:
        mask = df["regione"] == regione
        df_r = df[mask].copy()
        correct_date_all(df_r)
        df_clean = df_clean.append(df_r)
    return df_clean


def extract_color(df,color_dict):
    df["colore"] = [color_dict[d] for d in df["articolo"]]

def insert_data_nazione(df, regione):
    df_naz = df[df["livello"] == "nazionale"]
    df_r = df[df["regione"] == regione].reset_index()
    data_naz_ini = df_naz["datasetIni"].iloc[0]
    for i,data_inizio in df_r["datasetIni"].iteritems():
        last_index = df_r.index[-1]
        if i != last_index:
            df_naz["regione"] = regione
            data_inizio_suc = df_r.loc[i+1, "datasetIni"]
            if data_inizio_suc > data_naz_ini > data_inizio:
                df1 = df_r.loc[:i, :].copy()
                df3 = df_r.loc[i+1:, :].copy()
                df2 = df_naz.copy()
                break
    df_with_naz = pd.concat([df1,df2,df3]).copy()
    df_with_naz =  df_with_naz.drop(columns={"level_0"}).reset_index().copy()
    return df_with_naz

def fill_voids_cut_overlaps(df_r):
    for i, row in df_r.iterrows():
        last_index = df_r.index[-1]
        if i != last_index:
            df_r.loc[i,"datasetFin"] = df_r.loc[i+1, "datasetIni"]

def apply_insert_data_naz_fill_voids(df):
    regioni = df["regione"].unique()
    index = np.argwhere(regioni == "Intero territorio nazionale")
    regioni = np.delete(regioni, index)
    df_final = pd.DataFrame()
    for regione in regioni:
        df_r = insert_data_nazione(df, regione)
        fill_voids_cut_overlaps(df_r)
        df_final = df_final.append(df_r).copy()
    return df_final

def correct_last_date(df_r):
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if df_r["data_fine"].iloc[-1] < today:
        df_r["data_fine"].iloc[-1] = today

def extend_dates(df_r):
    df_r_extended = pd.DataFrame()
    for i, row in df_r.iterrows():
        start = row["data_inizio"]
        end = row["data_fine"]
        date_list = pd.date_range(start, end)
        new_df = pd.DataFrame()
        new_row = row
        for date in date_list[:-1]:
            new_row["data_inizio"] = date
            new_df = new_df.append(new_row)
        df_r_extended = df_r_extended.append(new_df)
    last_date = date_list[-1]
    new_row["data_inizio"] = last_date
    last_row = new_row
    df_r_extended = df_r_extended.append(last_row)
    return df_r_extended

def update_zone_esteso():
    data = get_data() # PRende i dati dal json
    df = create_properties_df(data)
    drop_and_rename_df(df) 
    convert_to_datetime(df)
    sort_and_rest_index(df)
    clean_date(df, "legNomeBre")
    clean_date(df, "legGU_ID")
    df_clean = clean_dataset_first(df)
    color_dict = {
        'art.1' : 'gialla',
        'art.2' : 'arancione',
        'art.3' : 'rossa',
        'art.1 comma 11':'bianca'
    }

    extract_color(df_clean, color_dict)
    df = apply_insert_data_naz_fill_voids(df_clean)
    df = df.drop(columns=["level_0", "versionID", "articolo", "legGU_ID", "nomeAutCom", "legNomeBre"])
    df.rename(columns={"datasetIni":"data_inizio", "datasetFin":"data_fine", "colore":"zona"}, inplace=True)
    regioni = df["regione"].unique()
    df_extended = pd.DataFrame()
    for regione in regioni:
        mask = df["regione"] == regione
        df_r = df[mask].copy()
        correct_last_date(df_r)
        df_extended = df_extended.append(extend_dates(df_r))
    return df_extended


######################################################################
#######  MERGING

def correct_zone(df_r, my_df_r):
    for index, row in df_r.iterrows():
        data = row["data"]
        my_row = my_df_r[my_df_r["data"] == data]
        my_zone = my_row["zona"].values
        if my_zone.size == 0 :
            my_zone = "unknown"
        df_r.loc[index, "zona"] = my_zone


def merge_covid_w_zone():
    df = pd.read_csv("https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv") 
    df["data"] = [ datetime.strptime(d, "%Y-%m-%dT%H:%M:%S").date() for d in df["data"]]
    my_df = pd.read_csv("data/zone_regioni_esteso.csv")
    my_df.rename(columns={"data_inizio":"data"}, inplace=True)
    my_df["data"] = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f").date() for d in my_df["data"]]  
    regioni = df["denominazione_regione"].unique()
    new_df = pd.DataFrame()
    for regione in regioni:
        df_r = df[df["denominazione_regione"] == regione].copy()
        my_df_r = my_df[my_df["regione"] == regione].copy()
        correct_zone(df_r, my_df_r)
        df_r = df_r[df_r["zona"]!= "unknown"].copy()
        new_df = new_df.append(df_r)
    new_df.drop(columns=["note", "note_test", "note_casi", "codice_nuts_1", "codice_nuts_2"], inplace=True)
    return new_df


##################################################################
######## PROVINCIE



def fig_sunburst(col,title):
    df_pr = pd.read_csv("data/provincie_w_population.csv")
    yesterday = datetime.today() - timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")
    df_pr = df_pr[(df_pr["data"] == yesterday) & (df_pr["totale_casi"]!=0)]
    fig_sun = px.sunburst(df_pr, path=['regione','provincia'],
                    values=col,
                    color=col,
                    range_color=[0,np.max((df_pr[col]))],
                    color_continuous_scale="ylorrd",
                    color_continuous_midpoint=np.average((df_pr[col])),
                    width=800, height=800,
                    branchvalues='total',
                    title=title
                    )
    return fig_sun


def last_update_choropleth():
    df_zone = pd.read_csv("data/zone_regioni_esteso.csv")
    last_update =  df_zone.iloc[-1,2].split(" ")[0]
    return last_update

def last_update_classificazione():
    df_regioni = pd.read_csv("data/ita_regioni_zone_correct.csv")
    last_update = df_regioni.iloc[-1,1]
    return last_update