import pandas as pd
import numpy as np
import json
from zipfile import ZipFile
import wget
from datetime import datetime, time, timedelta, date
import plotly.express as px
import scipy.stats as sps


#ritorna il file json
def get_data():
    url = 'https://github.com/pcm-dpc/COVID-19/raw/master/aree/geojson/dpc-covid-19-aree-nuove-g-json.zip'
    filenameZip = wget.download(url, out="data/zip")
    with ZipFile(filenameZip, 'r') as zipObj:
        zipObj.extractall(path="data/zip")
    #print('File is unzipped') 
    with open('data/zip/dpc-covid-19-aree-nuove-g.json') as file:
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
######## PROVINCE



def fig_sunburst(col,title):
    df_pr = pd.read_csv("data/province_w_population.csv")
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

##########################################################################
###### CALCOLO RT

def covid_regioni():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv",
        parse_dates=['data'],
        index_col=['data'],
        squeeze=True).sort_index()
    df.index = df.index.normalize()
    return df

def pierini_Rt(df, column, ignore=5,
               SI_sh=None, SI_ra=None, 
               conf_int=.99, smooth=7,
               #resample='last-day-of-week',
               func=np.mean, samples=100,
               plot_latest_Rt=False,
               plot=False, title='', ylim=(0, 5)):

    _lo = (1 - conf_int) / 2 * 100
    _hi = 100 - _lo
    
    df = df.copy(deep=True)
    T = df.index.size
    
    Rt0 = sps.halfnorm(0, 0.1).rvs(samples)
    
    less_than_zero = df[column]<0
    if less_than_zero.sum():
        print('Warning: negative values in incidence. Adjusting...')
        df.loc[less_than_zero, column] = 0

    if SI_sh is None or SI_ra is None:
        print('Warning: no serial interval given.')
        print('Assigning default one...')
        SI_sh = 1.87
        SI_ra = 0.28
    
    SI_dist = sps.gamma(a=SI_sh, scale=1/SI_ra)
    SI_x = np.arange(1, T+1, 1)
    SI_y = SI_dist.pdf(SI_x)

    pois_vars = np.zeros(shape=(T, samples))
    for t in range(T):
        pois_var = sps.poisson.rvs(df[column].values[t], size=samples)
        pois_vars[t,:] = pois_var

    Rt = np.zeros(shape=(T, samples))
    for t in range(T):
        if t < 1:
            continue
        if np.any(pois_vars[t] < ignore):
            Rt[t,:] = Rt0
            continue
        last = pois_vars[t]
        old = (pois_vars[:t] * SI_y[:t][::-1][:,None]).sum(axis=0)
        if np.any(old < ignore):
            Rt[t,:] = Rt0
            continue

        R_rvs = last / old
        Rt[t,:] = R_rvs
        
    Rt[0,:] = Rt[1:8].mean(axis=0)
    R = pd.DataFrame(columns=['R', 'sd', 'lo', 'hi'])
    R['R'] = np.median(Rt, axis=1)
    R['sd'] = np.std(Rt, axis=1)
    R['lo'], R['hi'] = np.percentile(Rt, [_lo, _hi], axis=1)
    R.index = df.index
    
    R_smoothed = R.rolling(smooth).mean()
    R_smoothed = R_smoothed[(smooth-1):]
    R_smo_len = R_smoothed.index.size
    idx_min = smooth // 2
    idx_max = R_smo_len + idx_min
    R_smoothed.index = R.index[idx_min:idx_max]
    
    latest_sh = R_smoothed.R[-1]**2 / R_smoothed.sd[-1]**2
    latest_ra = R_smoothed.R[-1] / R_smoothed.sd[-1]**2
    latest_Rd = sps.gamma(a=latest_sh, scale=1/latest_ra)
    latest_Rs = latest_Rd.rvs(size=10000)
    latest_Rx = np.linspace(latest_Rd.ppf(_lo/100), latest_Rd.ppf(_hi/100), 100)
    latest_Ry = latest_Rd.pdf(latest_Rx)
    latest_Rm = latest_Rd.mean()
    if latest_Rm > 1:
        p_val = latest_Rd.cdf(1)
    else:
        p_val = 1 - latest_Rd.cdf(1)
    
    if plot:
        ax = R_smoothed.plot(
            figsize=(12, 5), y='R', color='k',
            lw=1,
        )
        ax.fill_between(
            R_smoothed.index,
            R_smoothed.lo, R_smoothed.hi,
            color='k', alpha=.25,
            label=f'C.I. {conf_int:.0%}'
        )
        ax.axhline(1, color='r', ls='--')
        ax.legend()
        ax.set(
            title=f'{title} Rt estimation (Method: JARE-Pierini 2020)',
            ylabel='R(t)', xlabel='date',
            ylim=ylim
        )
        plt.show()
        
    if plot_latest_Rt:
        ax = az.plot_posterior(
            latest_Rs, ref_val=1,
            figsize=(8, 3),
            round_to=5,
            hdi_prob=conf_int,
            textsize=15
        )
        ax.text(
            .05, 1.1,
            f'$p$-val = {p_val:.3f}',
            fontsize=10, color='k',
         ha="center", va="center",
         bbox=dict(boxstyle="round",
                   ec=(.2, .2, .2),
                   fc=(.9, .9, .9, .5),
                   ),
            transform=ax.transAxes
        )
        ax.set(
            title=f'{title} Latest Rt {R_smoothed.index[-1].date()} (Method: JARE-Pierini 2020)'
        )
        plt.show()
    
    return R_smoothed, latest_Rs


def get_rt_index(): 
    ISS_sh = 1.87
    ISS_ra = 0.28
    rg = covid_regioni()
    df_rt = pd.DataFrame()
    for regione in rg.denominazione_regione.unique():
        _df = rg[rg.denominazione_regione==regione].copy(deep=True)
        _df.loc[_df.nuovi_positivi<0, 'nuovi_positivi'] = 0
        
        R, Rs = pierini_Rt(_df, 'nuovi_positivi', 
                    SI_sh=ISS_sh, SI_ra=ISS_ra,
                    smooth=7, samples=100, ignore=5)
        
        R["regione"] = regione    
        df_rt = pd.concat([R,df_rt])
    df_rt = df_rt.reset_index()    
    return df_rt



def merge_covid_w_rt(df_r, df_rt):
    df_rt["data"] = [datetime.strftime(d, "%Y-%m-%d") for d in df_rt["data"]]
    df_r["data"] = [datetime.strftime(d, "%Y-%m-%d") for d in df_r["data"]]
    df_r["indice_rt"] = 0
    na_dates = []
    date = df_r["data"].unique()
    regioni = df_r["denominazione_regione"].unique()
    for data in date:
        for regione in regioni:
            try: 
                mask_rt = (df_rt["data"] == data) & (df_rt["regione"] == regione)
                mask_r = (df_r["data"] == data) & (df_r["denominazione_regione"] == regione)
                df_r.loc[mask_r,"indice_rt"] = df_rt.loc[mask_rt, "R"].values[0]
            except:
                na_dates.append(data)
    na_dates = list(set(na_dates))
    return df_r, na_dates