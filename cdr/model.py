import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression,RidgeCV,Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.feature_selection import RFE
from sklearn.model_selection import train_test_split,cross_val_score
from process import makerdir
import seaborn as sns
import statsmodels.api as sm

class Model:
    def __init__(self,data,X_headers,Y_headers):
        self.data=data
        self.X_headers=X_headers
        self.Y_headers=Y_headers
 
    def correlation(self,o_path):
        self.data.corr(method ='pearson').to_csv(o_path)
    
    def corr_heatmap(self,df,o_path):
        plt.subplots(figsize=(90,90))
        plt.xticks(fontsize='60')
        plt.yticks(fontsize='60')
        sns.set(font_scale=2)
        sns.heatmap(df,cmap='coolwarm',annot=True,cbar=False)
        sns.heatmap(df, mask=df < 0.5,cmap='coolwarm',annot=True,cbar=False, annot_kws={"weight": "bold","size":100})
        sns.heatmap(df, mask=df > -0.5,cmap='coolwarm',annot=True,cbar=False, annot_kws={"weight": "bold","size":100})
        plt.savefig(o_path)

    def single_model_runner(self):
        for y in self.Y_headers:
            for x in self.X_headers:
                self.single_model(x,np.array(self.data[x]),y,np.array(self.data[y]))

    def multivariate_model_runner(self):
        for y in self.Y_headers:
            self.select_K(y,np.array(self.data[y]))

    def select_K(self,Y_name,Y_arr):
        model=Ridge()
        rfe=RFE(model,3,step=1) 
        res=rfe.fit(self.data[self.X_headers],Y_arr)

        names=pd.DataFrame(self.X_headers)
        rankings=pd.DataFrame(res.ranking_)
        ranked=pd.concat([names,rankings], axis=1)
        ranked.columns=["Feature","Rank"]
        selected=ranked.loc[ranked['Rank']==1]

        fname='results/multivariate_model/%s'%Y_name
        X_name='Best %d Features for %s:\n' %(len(selected),Y_name)
        X_name+=','.join(selected['Feature'])
        
        return self.multivariate_model(X_name,self.data[selected['Feature']],Y_name,Y_arr,fname)
    
    def multivariate_model(self,X_name,X_arr,Y_name,Y_arr,fname):
        return self.build(X_name,X_arr,Y_name,Y_arr,fname)

    def single_model(self,X_name,X_arr,Y_name,Y_arr):
        fname='results/single_model/%s_%s'%(X_name,Y_name)
        return self.build(X_name,X_arr.reshape(-1,1),Y_name,Y_arr,fname)

    def build(self,X_name,X_arr,Y_name,Y_arr,fname):
        model=RidgeCV(scoring='r2').fit(X_arr, Y_arr)
        tree=DecisionTreeRegressor().fit(X_arr,Y_arr)
        y_pred=model.predict(X_arr)
        score=r2_score(Y_arr,y_pred)
        if self.random:
            return score
        if score>=0:
            f=open(fname+'.txt','w+')
            f.write("Results for %s vs. %s\n"%(X_name,Y_name))
            f.write("Metrics:\nR2 Score: %f\nMean Squared Error: %f\n" % (score,mean_squared_error(Y_arr,y_pred)))
            importance=' '.join('%.2f' % coef for coef in tree.feature_importances_)
            f.write('Feature importance %s\n'%importance)
            f.close()
            
    def plot(self,X_name,X_arr,Y_name,Y_arr,y_lin_reg,fname):
        plt.subplots(figsize=(10,10))
        plt.scatter(X_arr, Y_arr)
        plt.xlabel(X_name)
        plt.ylabel(Y_name)
        plt.plot(X_arr, y_lin_reg, c = 'r')        
        plt.savefig(fname+".png")
        plt.close()