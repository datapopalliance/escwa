from process import read,save,read_output
import pandas as pd
import numpy as np

def mb(df,o_path):
    df = df.groupby(['MOUHAFAZA','YEAR','KAZA'],as_index=False).agg({
        'UPLINK_MB':'sum',
        'DOWNLINK_MB':'sum',
        'TOTAL_MB':'sum',
    })
    df['ALFA_UP/DOWN']=df['ALFA_UPLINK_MB'].astype(float)/df['ALFA_DOWNLINK_MB'].astype(float)
    df['ALFA_UP/TOTAL']=df['ALFA_UPLINK_MB'].astype(float)/df['ALFA_TOTAL_MB'].astype(float)
    df['ALFA_DOWN/TOTAL']=df['ALFA_DOWNLINK_MB'].astype(float)/df['ALFA_TOTAL_MB'].astype(float)
    save(df,o_path)