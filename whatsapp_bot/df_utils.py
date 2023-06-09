import pandas as pd
import numpy as np

def open_directivos_EBR(url, dre_name=None, ugel_cod=None, var_start=None, var_end=None, test=False):
    if test==True:
        df=url.copy()
    else:
        text = url.rsplit('/', 1)[0]
        df=pd.read_csv(text+"/export?format=csv", converters={0:str,1:str,"CODOOII":str})
        list_name=df.columns.str.lower().to_list()
        df.columns=list_name

        if dre_name!=None:
            df=df[df.dre==dre_name].copy()
        else:
            if ugel_cod!=None:
                df=df[df.codooii==ugel_cod].copy()
            else:
                df=df.copy()
        df=df.sort_values("codooii").iloc[var_start:var_end].reset_index().rename({"index":"index_o"},axis=1)
    return df

def change_report(url_rep_1, url_rep_2):
    r1=(open_clean_var(url_rep_1).
        query('cod_unico!="000"', engine='python')
        [['CODDRE', 'DRE', 'codooii','cod_unico','DNIDIRECTIVO','phone_numbers', 'statusdes','sec_gen', 'sec_met','envio']].
        copy()
       )
    r2=(open_clean_var(url_rep_2).
        query('cod_unico!="000"', engine='python')
        [['CODDRE', 'DRE', 'codooii','cod_unico','DNIDIRECTIVO','phone_numbers', 'statusdes','sec_gen', 'sec_met']].
        copy()
       )
    r2.columns=['CODDRE_2', 'DRE_2', 'codooii_2','cod_unico_2','DNIDIRECTIVO_2', 'phone_numbers_2', 'statusdes_2','sec_gen_2', 'sec_met_2']
    
    r3=r1.set_index('cod_unico').merge(r2.set_index('cod_unico_2'), right_index=True, left_index=True, how='outer', validate='1:1', indicator=True)
    r3['envio']=np.where(r3.envio.isna(),0, r3.envio)
    r3['statusdes']=np.where(r3.statusdes.isna(),"NUEVO", r3.statusdes)
    print(r3.groupby(['statusdes','statusdes_2','envio']).size().unstack())
    r3=r3[['CODDRE_2', 'DRE_2', 'codooii_2','DNIDIRECTIVO_2', 'phone_numbers_2', 'statusdes_2','sec_gen_2', 'sec_met_2','envio']].reset_index()
    r3.columns=['cod_unico','CODDRE', 'DRE', 'codooii','DNIDIRECTIVO','phone_numbers', 'statusdes','sec_gen', 'sec_met','envio']
    
    return r3

def open_clean_var(url):
    text = url.rsplit('/', 1)[0]
    df=pd.read_csv(text+"/export?format=csv", converters={0:str, 2:str,5:str,6:str,7:str,8:str,13:str,14:str})
    for p in ['cm_ini','cm_pri', 'cm_sec']:
        df[p]=df[p].replace("","0", regex=True)
    df["cod_unico"]=df.cm_ini+df.cm_pri+df.cm_sec+df.DNIDIRECTIVO
    df['statusdes']=df['statusdes'].str.upper().str.strip().replace("EN ","",regex=True)
    df=df.rename({'TELEFONOPERSONAL':'phone_numbers','CODUGEL':'codooii'},axis=1)
    
    return df

def clean_numbers(df_o):
    df=df_o.copy()
    df["phone_l"]=df.phone_numbers.str.strip().str.len()
    df=df.query('phone_l==9 & phone_numbers!="999999999" & phone_numbers!="123456789"', engine='python').copy()
    df['phone_numbers']=df['phone_numbers'].astype(int)
    del df["phone_l"]
    
    return df

def open_clean_var_seguimiento(url):
    text = url.rsplit('/', 1)[0]
    df=pd.read_csv(text+"/export?format=csv", skiprows=1, usecols=[3,4,5,6,7,8,9,10,11,23,52,53,57,58,59], converters={3:str,5:str,6:str,7:str,8:str,9:str,10:str,11:str,52:str,53:str})
    df.columns=['CODDRE','DRE','codooii','ugel','cod_local','cod_unico_0','cm_ini','cm_pri', 'cm_sec','alerta','phone_numbers','DNIDIRECTIVO','statusdes','sec_gen', 'sec_met']
    for p in ['cm_ini','cm_pri', 'cm_sec']:
        df[p]=df[p].replace("","0", regex=True)
    df["cod_unico"]=df.cm_ini+df.cm_pri+df.cm_sec+df.DNIDIRECTIVO
    df['alerta']=df['alerta'].str.upper().str.strip().replace("Í","I",regex=True)
    
    return df

def cleaning_report_status_df(url, estado, dre_name=None, ugel_cod=None, tipologia=None,var_start=None, var_end=None, test=False, first_rep=False):
    if test==True:
        df_3=url.copy()
    else:
        if first_rep==True:
            df_3=open_clean_var_seguimiento(url)[['CODDRE', 'DRE', 'codooii','cod_unico','DNIDIRECTIVO','phone_numbers', 'statusdes','sec_gen', 'sec_met','alerta']].copy()
            df_3["envio"]=0
        else:
            df_3=url.query('envio==0').copy()
        
        if dre_name!=None:
            df_3=df_3[df_3.dre==dre_name].copy()
        else:
            if ugel_cod!=None:
                df_3=df_3[df_3.codooii==ugel_cod].copy()
            else:
                df_3=df_3.copy()
        
        if estado=="PENDIENTE":
            df_3=df_3.query('statusdes==@estado', engine='python').copy()
        if estado=="PROCESO":
            ##creamos la tipología
            df_3['tipo']=0
            df_3['tipo']=np.where((df_3.sec_gen=="FALSO") &(df_3.sec_met=="VERDADERO"),1,df_3.tipo)
            df_3['tipo']=np.where((df_3.sec_gen=="VERDADERO") &(df_3.sec_met=="FALSO"),2,df_3.tipo)
            df_3['tipo']=np.where((df_3.sec_gen=="VERDADERO") &(df_3.sec_met=="VERDADERO"),3,df_3.tipo)
            df_3['tipo']=np.where((df_3.alerta=="SI"), 4, df_3.tipo)
            ## filtramos
            df_3=df_3.query('statusdes==@estado & tipo==@tipologia', engine='python')
        elif estado=="TODOS":
            ##creamos la tipología
            df_3['tipo']=0
            df_3['tipo']=np.where((df_3.alerta=="SI"), 4, df_3.tipo)
            ## filtramos
            df_3=df_3.query('tipo==@tipologia', engine='python')
            
        
        ## limpiamos los telefonos que no corresponden a números reales
        df_3=clean_numbers(df_3).copy()     
        df_3=df_3.sort_values("DNIDIRECTIVO").iloc[var_start:var_end].reset_index().rename({"index":"index_o"},axis=1)
        
    return df_3


def get_excel_txt(url, seguimiento_text=False, estado=None, tipologia=None):
    text = url.rsplit('/', 1)[0]
    if seguimiento_text==True:       
        ## cleaning the data
        df=pd.read_csv(text+"/export?format=csv"+"&gid="+str(1620900866))
        df['enviar']=df['enviar'].str.upper().str.strip().replace(["Ï","Í","Ì"],"I",regex=True)
        if estado=="PENDIENTE":
            df['Estado']=df['Estado'].str.upper().str.strip()
            df=df[(df.Estado==estado)&(df.enviar=='SI')].copy()
        if estado=="TODOS":
            df=df[(df.Tipologia==str(tipologia))&(df.enviar=='SI')].copy()
        else:            
            df=df[(df.Tipologia==str(tipologia))&(df.enviar=='SI')].copy()
            if tipologia ==0:
                df=df.iloc[0:1]
        
        df["text"]=df["text"]+" \n"
        df=df.iloc[:,4:].copy()
        
    else:        
        ## cleaning the data
        df=pd.read_csv(text+"/export?format=csv")

        df.columns=['text','enviar']
        df['enviar']=df['enviar'].str.upper().str.strip().replace(["Ï","Í","Ì"],"I",regex=True)
        df=df[(df.text.notna())&(df.enviar=='SI')].copy()
        df["text"]=df["text"]+" \n"
        
    return df

def delay_list(low_time, high_time, size_list):
    rng = np.random.default_rng()
    delay_l = rng.integers(low=low_time, high=high_time, size=size_list).tolist()    
    return delay_l



