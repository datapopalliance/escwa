from process import read,read_excel,save,read_output,save_plot,makepdir,read_output
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from datetime import datetime
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
days=['MON','TUES','WED','THURS','FRI','SAT','SUN']

def weekday(row):
    day=days[datetime(row['YEAR'],row['MONTH'],row['DAY']).weekday()]
    if row['HOLIDAY']:
        row['DAY_TYPE']='HOLIDAY'
    elif day=='SAT' or day=='SUN':
        row['DAY_TYPE'] = 'WEEKEND'
    else:
        row['DAY_TYPE'] = 'WEEKDAY'
    return row

def set_weekday():
    df=read('daily.csv')
    df=df.apply(lambda row:weekday(row),axis=1)
    save(df,'daily.csv')

def indicators():
    df=read_output('daily.csv')
    df2=pd.DataFrame()
    for year in np.unique(df['YEAR']):
        sub=df[df['YEAR']==year]
        ramadan=sub[sub['RAMADAN']]['NB_CALLS'].mean()/sub[sub['RAMADAN']==False]['NB_CALLS'].mean()
        weekend=sub[sub['TYPE']=='WEEKEND']['NB_CALLS'].mean()/sub[sub['TYPE']=='WEEKDAY']['NB_CALLS'].mean()        
        holiday=sub[sub['HOLIDAY']]['NB_CALLS'].mean()/sub[sub['HOLIDAY']==False]['NB_CALLS'].mean()        
        df2=df2.append({
            'YEAR':year,
            'RAMADAN_RATIO':ramadan,
            'HOLIDAY_RATIO':holiday,
            'WEEKEND_RATIO':weekend
        },ignore_index=True)
    
    save(df2,'refugee_activity.csv')

def boxplot():
    df=read_output('daily.csv')
    df.boxplot(column=['NB_CALLS'],by='DAY_TYPE', figsize = (20,20))
    plt.savefig('boxplot.jpg')

def plot_total():
    df=read_output('daily.csv')
    df=df.groupby(['DAY_TYPE'],as_index=False).agg({'NB_CALLS':'mean'})
    df.plot.bar(x = 'DAY_TYPE', y = 'NB_CALLS', title = 'Histogram of Variation of Number of Calls by Day Type', figsize = (20,20))
    plt.savefig('distribution.jpg')