import pandas as pd
import numpy as np

def open_directivos_EBR(url, dre_name=None, ugel_cod=None, var_start=None, var_end=None, test=False):
    if test==True:
        df=url.copy()
    else:
        text = url.rsplit('/', 1)[0]
        ## cleaning the data
        df=pd.read_csv(text+"/export?format=csv", converters={0:str,1:str,9:str})

        if dre_name!=None:
            df=df[df.DRE==dre_name].copy()
        else:
            if ugel_cod!=None:
                df=df[df.codooii==ugel_cod].copy()
            else:
                df=df.copy()
            df=df.sort_values("codooii").iloc[var_start:var_end].reset_index().rename({"index":"index_o"},axis=1)
    return df

def get_excel_txt(url):
    text = url.rsplit('/', 1)[0]
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