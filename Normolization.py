# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 09:42:53 2019

@author: yifan.gong
"""

import numpy as np
from copy import deepcopy

class Normolize(object):
    def __init__(self,X:np.ndarray):
        self.X = deepcopy(X.reshape(-1,1))
    
    def MAD(self,n = 3):
        n = abs(n)
        X = self.X
        med = np.median(X)
        new_med = np.median(abs(X-med))
        ub = med + n*new_med
        bb = med - n*new_med
        return np.clip(X,bb,ub)
    
    def winsorize(self,quantile = [0.1,0.9]):
        X = self.X
        if quantile[0]<0 or quantile[1]>1:
            raise ValueError('Quantiles must be in the range [0, 1].')
        bb = np.quantile(X,quantile[0])
        ub = np.quantile(X,quantile[1])
        return np.clip(X,bb,ub)
    
    def Z_score(self):
        X = self.X
        mean = np.mean(X)
        std = np.std(X,ddof = 1)
        return (X-mean)/std
        
#%%
if __name__ == '__main__':
    import random
    from matplotlib import pyplot as plt
    from LinearRegression import LinearRegress
    
    Xt1 = [random.random()*10 for i in range(50)]
    Yt1 = [random.uniform(7,12)*val+random.uniform(-10,10) for val in Xt1]
    Xt2 = [random.random()*10 for i in range(5)]
    Yt2 = [random.uniform(7,12)*val+random.uniform(0,1000) for val in Xt2]
    X = Xt1+Xt2
    Y = Yt1+Yt2

    
    fig1 = plt.figure(figsize = (2,6),dpi = 200)
    
    ax0 = fig1.add_subplot(511)
    ax0.scatter(X,Y,edgecolor='none',s = 5)
    ax0.tick_params(labelsize = 5)
    
    n = Normolize(np.asarray(Y))
    
    Y1 = n.MAD()
    ax1 = fig1.add_subplot(512)
    ax1.scatter(X,Y1,edgecolor='none',s = 5)
    ax1.tick_params(labelsize = 5)
    
    Y2 = n.winsorize()
    ax2 = fig1.add_subplot(513)
    ax2.scatter(X,Y2,edgecolor='none',s = 5)
    ax2.tick_params(labelsize = 5)
    
    Y3 = n.Z_score()
    ax3 = fig1.add_subplot(514)
    ax3.scatter(X,Y3,edgecolor='none',s = 5)
    ax3.tick_params(labelsize = 5)
    
    Y4 = n.MAD()
    n1 = Normolize(np.asarray(Y4))
    Y4 = n1.Z_score()
    ax4 = fig1.add_subplot(515)
    ax4.scatter(X,Y3,edgecolor='none',s = 5)
    ax4.tick_params(labelsize = 5)
#%%    
    fig2 = plt.figure(figsize = (2,6),dpi = 200)
    
    l1 = LinearRegress(np.mat(X).reshape(-1,1),np.mat(Y))
    alpha1,beta1,epi1 = l1.Mestimator()
    Y_predict1 = beta1*X+alpha1
    ax5 = fig2.add_subplot(311)
    ax5.scatter(X,Y,edgecolor='none',s = 5)
    ax5.plot(X,Y_predict1[0],c = 'r',linewidth = 0.5)
    
    l2 = LinearRegress(np.mat(X).reshape(-1,1),np.mat(Y1))
    alpha2,beta2,epi2 = l2.Mestimator()
    Y_predict2 = beta2*X+alpha2
    ax6 = fig2.add_subplot(312)
    ax6.scatter(X,Y1,edgecolor='none',s = 5)
    ax6.plot(X,Y_predict2[0],c = 'r',linewidth = 0.5)
    
    l3 = LinearRegress(np.mat(X).reshape(-1,1),np.mat(Y4))
    alpha3,beta3,epi3 = l3.Mestimator()
    Y_predict3 = beta3*X+alpha3
    ax7 = fig2.add_subplot(313)
    ax7.scatter(X,Y4,edgecolor='none',s = 5)
    ax7.plot(X,Y_predict3[0],c = 'r',linewidth = 0.5)
    
    