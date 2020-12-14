from process import read,save,read_output,save_plot,makepdir
import numpy as np
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches

def age_grp(row):
    a=row['AGE']
    if a<20:
        row['AGE_GROUP'] = '<20'
    elif a>=70:
        row['AGE_GROUP'] = '>69'
    else:
        for r in ranges:
            r1=int(r.split('-')[0])
            r2=int(r.split('-')[1])
            if a>=r1 and a<=r2:
                row['AGE_GROUP']=r
    return row   

def build():
    df=read("age_pyramid.csv")
    df=df.apply(lambda row:age_grp(row),axis=1)
    df=df.groupby(['YEAR','AGE_GROUP','GENDER'],as_index=False).agg({'NB_CALLS':'sum'})
    structure(df)

def structure(df):
    df2=pd.DataFrame()
    for year in np.unique(np.array(df['YEAR'])):
        sub=df[df['YEAR'] == year]
        for age in np.unique(np.array(sub['AGE_GROUP'])):
            m=-1*sub[(sub['YEAR']==year)&(sub['AGE_GROUP']==age)&(sub['GENDER']=='M')]['NB_CALLS'].values.item()
            f=sub[(sub['YEAR']==year)&(sub['AGE_GROUP']==age)&(sub['GENDER']=='F')]['NB_CALLS'].values.item()
            df2=df2.append({'YEAR':year,'AGE_GROUP':age,'MALE':m,'FEMALE':f},ignore_index=True)        
    save(df2,'pop_pyramid.csv')

def plot():
    makepdir('pop_pyramid')
    df=read_output('pop_pyramid.csv')
    for year in years:
        sub=df[df.YEAR==year]
        plot_year(year,sub)

def plot_year(year,df):
    age=df['AGE_GROUP'][::-1]
    plt.subplots(figsize=(20,20))
    bar_plot = sns.barplot(x='MALE',y='AGE_GROUP',data=df,order=age,lw=0,color='#1f77b4')
    bar_plot = sns.barplot(x='FEMALE',y='AGE_GROUP',data=df,order=age,lw=0,color='#ff7f0e')
    bar_plot.set(xlabel="Population (Based on Call activity)", ylabel="Age-Group", title = "Population Pyramid in %d"%year)
    female_patch = mpatches.Patch(color='#ff7f0e', label='FEMALE')
    male_patch = mpatches.Patch(color='#1f77b4', label='MALE')
    plt.legend(handles=[male_patch,female_patch])
    save_plot('pop_pyramid/%d'%year)