from variables import CURRENT,ALFA,DPATH,OPATH,TOUCH
from process import read,save,read_output
import pandas as pd
import numpy as np

def sites_per_kaza(df,o_path):
    o=pd.DataFrame()
    kazas=np.unique(df['KAZA'])
    for year in years:
        for kaza in kazas:
            sub=df[(df['KAZA']==kaza) & (df['YEAR']==year)]
            o=o.append({'YEAR':year,'KAZA':kaza,'NB_SITES':len(sub)},ignore_index=True)
    save(o,o)

def calls_cleanup(df):
    return df.groupby(['MOUHAFAZA','YEAR','KAZA'],as_index=False).agg({'NB_CALLS':'sum','DURATION_IN_SEC':'sum','DURATION_IN_MIN':'sum',})

def economics(in_df,out_df,o_path):
    in_to_out=pd.DataFrame()
    for _,row in in_df.iterrows():
        dic={}
        dic['YEAR']=row['YEAR']
        dic['MOUHAFAZA']=row['MOUHAFAZA']
        dic['KAZA']=row['KAZA']
        out=out_df[(out_df['KAZA']==row['KAZA'])&(out_df['YEAR']==row['YEAR'])]
        dic['NB_RATIO']=out['NB_CALLS'].values.item()/row['NB_CALLS']
        dic['DURATION_RATIO']=out['DURATION_IN_SEC'].values.item()/row['DURATION_IN_SEC']
        dic['AVG_IN_DURATION_SEC']=row['DURATION_IN_SEC']/row['NB_CALLS']
        dic['AVG_IN_DURATION_MIN']=row['DURATION_IN_MIN']/row['NB_CALLS']
        dic['AVG_OUT_DURATION_SEC']=out['DURATION_IN_SEC'].values.item()/out['NB_CALLS'].values.item()
        dic['AVG_OUT_DURATION_MIN']=out['DURATION_IN_MIN'].values.item()/out['NB_CALLS'].values.item()
        
        in_to_out=in_to_out.append(dic,ignore_index=True)

    save(in_to_out,o_path)

def get_population(df,row):
    gov=df[(df['MOUHAFAZA']==row['MOUHAFAZA'])&(df['YEAR']==row['YEAR'])]
    total=gov['NB_CALLS'].sum()
    row['POPULATION']=row['NB_CALLS']/total
    return row

def annual_population(in_df,out_df,o_path):
    in_df=calls_cleanup(in_df)
    out_df=calls_cleanup(out_df)
    df=in_df.append(out_df, sort = False)
    df=df.groupby(['MOUHAFAZA','YEAR','KAZA'],as_index=False).agg({'NB_CALLS':'sum'})
    df=df.apply(lambda row: get_population(df,row), axis=1)
    save(df,o_path)

def get_variation(mob,row):
    prev_year=mob[(mob['KAZA'] == row['KAZA']) & (mob['YEAR']==(row['YEAR']-1))]
    prev_pop=prev_year.loc[prev_year.index[0],'POPULATION']
    row['MOBILITY'] = ((row['POPULATION']-prev_pop)/prev_pop) * 100
    return row

def annual_mobility():
    mob=read_output('population.csv')
    mob=mob.apply(lambda row: get_variation(mob,row), axis=1)
    save(mob,'mobility.csv')