import pandas as pd
import numpy as np

def open_directivos_EBR(url, dre_name=None, ugel_cod=None, var_start=None, var_end=None, test=False, gid=None):
    if test==True:
        df=url.copy()
    else:
        text = url.rsplit('/', 1)[0]
        if gid!=None:
          df=pd.read_csv(text+"/export?format=csv"+"&gid="+str(gid))
        else:
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
        df=clean_numbers(df)
    return df

def open_family(url, dre_name=None, ugel_cod=None, var_start=None, var_end=None, test=False, tipologia=None):
    if test==True:
        df=url.copy()
    else:
        text = url.rsplit('/', 1)[0]
        df=pd.read_csv(text+"/export?format=csv", converters={"celular_rl":str})
        list_name=df.columns.str.lower().to_list()
        df.columns=list_name
        df=df.rename({"estado de acreditación":"acreditacion"},axis=1)
        
        if dre_name!=None:
            df=df[df.dre==dre_name].copy()
        else:
            if ugel_cod!=None:
                df=df[df.codooii==ugel_cod].copy()
            else:
                df=df.copy()

        ## creamos la tipologia
        df['tipo']=0
        df['tipo']=np.where((df.estado=="Apta para envío") & (df.acreditacion=="Acreditado"), 1, df.tipo)
        df['tipo']=np.where((df.estado=="Apta para envío") & (df.acreditacion=="En proceso"), 2, df.tipo)
        df['tipo']=np.where((df.estado=="Apta para envío") & (df.acreditacion=="Pendiente"), 3, df.tipo)
        df['tipo']=np.where((df.estado=="Apta para envío") & (df.acreditacion=="Validado"), 4, df.tipo)
        df['tipo']=np.where((df.estado=="Pendiente de envío") & (df.acreditacion=="Acreditado"), 5, df.tipo)
        df['tipo']=np.where((df.estado=="Pendiente de envío") & (df.acreditacion=="En proceso"), 6, df.tipo)
        df['tipo']=np.where((df.estado=="Pendiente de envío") & (df.acreditacion=="No acreditado"), 7, df.tipo)
        df['tipo']=np.where((df.estado=="Pendiente de envío") & (df.acreditacion=="Pendiente"), 8, df.tipo)
        df['tipo']=np.where((df.estado=="Pendiente de envío") & (df.acreditacion=="Validado"), 9, df.tipo)
        
        df=df.query('tipo==@tipologia', engine='python').iloc[var_start:var_end].reset_index().rename({"index":"index_o"},axis=1)
    
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
    if df.phone_numbers.dtype == "int64":
        df["phone_numbers"]=df.phone_numbers.astype(str)
    
    elif df.phone_numbers.dtype == "float64":
        df["phone_numbers"]=df.phone_numbers.astype(int).astype(str)
    
    df["phone_l"]=df.phone_numbers.str.strip().str.len()
    df1=df.query('phone_l==9 & phone_numbers!="999999999" & phone_numbers!="123456789"', engine='python').copy()
    df['phone_numbers']=df['phone_numbers'].astype(int)
    del df["phone_l"]
    
    report_n=df.phone_numbers.count()-df1.phone_numbers.count()
    print(f"Se eliminaron de la base de datos {report_n} números telefónicos inválidos")
    
    return df

def open_clean_var_seguimiento(url):
    text = url.rsplit('/', 1)[0]
    df=pd.read_csv(text+"/export?format=csv", skiprows=1,  usecols=[3,4,5,6,8,9,10,11,12,26,32,33,34,44,16,17,18,20,21],
               converters={3:str,5:str,6:str,8:str,9:str,10:str,11:str,12:str,44:str,20:str,21:str})
    df.columns=['CODDRE','DRE','codooii','ugel','cod_local','cod_unico_0','cm_ini','cm_pri','cm_sec', 'ape_p','ape_m','nombre', 'DNIDIRECTIVO','phone_numbers','sec_met','registrado','proceso','pendiente','alerta']
    for p in ['cm_ini','cm_pri', 'cm_sec']:
        df[p]=df[p].replace("","0", regex=True)
    df["cod_unico"]=df.cm_ini+df.cm_pri+df.cm_sec+df.DNIDIRECTIVO
    df['alerta']=df['alerta'].str.upper().str.strip().replace("Í","I",regex=True)
    df['sec_met']=df['sec_met'].str.upper().str.strip().replace(["FALSO","VERDADERO"],["0","1"],regex=True).fillna("0").astype(int)
    for q in ['registrado','proceso', 'pendiente']:
      df[q]=df[q].fillna("0").astype(int)

    return df

def cleaning_report_status_df(url, dre_name=None, ugel_cod=None, tipologia=None,var_start=None, var_end=None, test=False, first_rep=False):
    if test==True:
        df_3=url.copy()
    else:
        if first_rep==True:
            df_3=open_clean_var_seguimiento(url)[['CODDRE', 'DRE', 'codooii','cod_unico','DNIDIRECTIVO','phone_numbers','proceso','pendiente', 'sec_met','alerta']].copy()
            df_3["envio"]=0
        else:
            df_3=url.query('envio==0').copy()

        if dre_name!=None:
            df_3=df_3[df_3.DRE==dre_name].copy()
        else:
            if ugel_cod!=None:
                df_3=df_3[df_3.codooii==ugel_cod].copy()
            else:
                df_3=df_3.copy()

    ## creamos la tipologia
    df_3['tipo']=0
    df_3['tipo']=np.where((df_3.sec_met==1), 1, df_3.tipo)
    df_3['tipo']=np.where((df_3.proceso==1) & (df_3.sec_met==0), 2, df_3.tipo)
    df_3['tipo']=np.where((df_3.pendiente==1) & (df_3.sec_met==0), 4, df_3.tipo)
    df_3['tipo2']=np.where((df_3.alerta=="SI"), 5, 0)

    if tipologia==5:
      df_3=df_3.query('tipo2==@tipologia', engine='python')
    else:
      df_3=df_3.query('tipo==@tipologia', engine='python')

    ## limpiamos los telefonos que no corresponden a números reales
    df_3=clean_numbers(df_3).copy()
    df_3=df_3.sort_values("DNIDIRECTIVO").iloc[var_start:var_end].reset_index().rename({"index":"index_o"},axis=1)

    return df_3


def get_excel_txt(url, seguimiento_text=False, tipologia=None, familias_wa=None):
    text = url.rsplit('/', 1)[0]
    if seguimiento_text==True:       
        ## cleaning the data
        df=pd.read_csv(text+"/export?format=csv"+"&gid="+str(1620900866))
        df['enviar']=df['enviar'].str.upper().str.strip().replace(["Ï","Í","Ì"],"I",regex=True)
        
        df=df[(df.Tipologia==str(tipologia))&(df.enviar=='SI')].copy()
        
        df["text"]=df["text"]+" \n"
        df=df.iloc[:,4:].copy()
        
    if familias_wa==True:
        df=pd.read_csv(text+"/export?format=csv"+"&gid="+str(1806006055))
        df['enviar']=df['enviar'].str.upper().str.strip().replace(["Ï","Í","Ì"],"I",regex=True)
        
        df=df[(df.Tipologia==tipologia)&(df.enviar=='SI')].copy()
        df["text"]=df["text"]+" \n"
        df=df.iloc[:,3:].copy()
        
    else:        
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







