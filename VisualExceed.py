# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 10:56:10 2019

@author: yifan.gong
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdate
import datetime
#使用Df数据，计算净值PnL图数据
def Asset_to_list_Df(Df,asset = 100000000):
    datelist = [key for key in Df.keys()]
    Asset1 = [v['Asset']/asset for v in Df.values()]
    return datelist,Asset1
#使用Df数据，计算收益率（加算）图数据
def Assetpct_to_list_Df(Df,asset = 100000000):
    datelist = [key for key in Df.keys()]
    temp1 = [v['Assetpct'] for v in Df.values()]
    Assetpct1 = [1+sum(temp1[:i]) for i in range(len(temp1))]
    return datelist,Assetpct1

def plot_Exceed_Df(Df,DfAll,title = 'fig'):
    datelist,AssetpctAll = Assetpct_to_list_Df(DfAll)   
    fig1 = plt.figure(figsize = (16,9),dpi = 200)
    ax1 = fig1.add_subplot(111)    
    Assetpct = []
    Aex = []
    Ex = []
    for i in range(len(Df)):
        Assetpct.append(0)
        Aex.append(0)
        Ex.append(0)
        _,Assetpct[i] = Assetpct_to_list_Df(Df[i])
        Aex[i] = [Assetpct[i][j]- AssetpctAll[j] for j in range(len(AssetpctAll))]
        Ex[i] = ax1.plot(datelist[:],Aex[i][:],label = '第'+str(i+1)+'组')
    ax1.legend(loc="best")
    ax1.set_title(title,fontsize=16)
    xt = np.arange(0,int(len(datelist)/10)*10,int(len(datelist)/100)*4)
    xtick = [datelist[x] for x in xt]
    ax1.set_xticks(xtick)
    plt.xticks(rotation = 45)
    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
    plt.legend(fontsize = 15)
    return fig1
    
def plot_PnL_Df(Df,DfAll,title = 'fig'):
    datelist,AssetAll = Asset_to_list_Df(DfAll)   
    fig1 = plt.figure(figsize = (16,9),dpi = 200)
    ax1 = fig1.add_subplot(111)    
    Asset = []
    Aex = []
    Ex = []
    for i in range(len(Df)):
        Asset.append(0)
        Aex.append(0)
        Ex.append(0)
        _,Asset[i] = Asset_to_list_Df(Df[i])
        Aex[i] = [Asset[i][j] for j in range(len(AssetAll))]
        Ex[i] = ax1.plot(datelist[:],Aex[i][:],label = '第'+str(i+1)+'组')
    ax1.legend(loc="best")
    ax1.set_title(title,fontsize=16)
    xt = np.arange(0,int(len(datelist)/10)*10,int(len(datelist)/100)*4)
    xtick = [datelist[x] for x in xt]
    ax1.set_xticks(xtick)
    plt.xticks(rotation = 45)
    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
    plt.legend(fontsize = 15)
    return fig1
#%%
#使用Nv数据，计算净值PnL图数据
def Asset_to_list_Nv(Nv,asset = 100000000):
    datelist = [key for key in Nv.keys()]
    Asset1 = [v/asset for v in Nv.values()]
    return datelist,Asset1
#使用Nv数据，计算收益率（加算）图数据
def Assetpct_to_list_Nv(Nv,asset = 100000000):
    datelist = [key for key in Nv.keys()]
    values = list(Nv.values())
    temp1 = [0]
    for i in range(len(values)-1):
        temp1.append(values[i+1]/values[i]-1)
    Assetpct1 = [1+sum(temp1[:i]) for i in range(len(temp1))]
    return datelist,Assetpct1

def plot_Exceed_Nv(Nv,NvAll,title = 'fig'):
    datelist,AssetpctAll = Assetpct_to_list_Nv(NvAll)   
    fig1 = plt.figure(figsize = (16,9),dpi = 200)
    ax1 = fig1.add_subplot(111)    
    Assetpct = []
    Aex = []
    Ex = []
    for i in range(len(Nv)):
        Assetpct.append(0)
        Aex.append(0)
        Ex.append(0)
        _,Assetpct[i] = Assetpct_to_list_Nv(Nv[i])
        Aex[i] = [Assetpct[i][j]- AssetpctAll[j] for j in range(len(AssetpctAll))]
        Ex[i] = ax1.plot(datelist[:],Aex[i][:],label = '第'+str(i+1)+'组')
    ax1.legend(loc="best")
    ax1.set_title(title,fontsize=16)
    xt = np.arange(0,int(len(datelist)/10)*10,int(len(datelist)/100)*4)
    xtick = [datelist[x] for x in xt]
    ax1.set_xticks(xtick)
    plt.xticks(rotation = 45)
    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
    plt.legend(fontsize = 15)
    return fig1
    
def plot_PnL_Nv(Nv,NvAll,title = 'fig'):
    datelist,AssetAll = Asset_to_list_Nv(NvAll)   
    fig1 = plt.figure(figsize = (16,9),dpi = 200)
    ax1 = fig1.add_subplot(111)    
    Asset = []
    Aex = []
    Ex = []
    for i in range(len(Nv)):
        Asset.append(0)
        Aex.append(0)
        Ex.append(0)
        _,Asset[i] = Asset_to_list_Nv(Nv[i])
        Aex[i] = [Asset[i][j] for j in range(len(AssetAll))]
        Ex[i] = ax1.plot(datelist[:],Aex[i][:],label = '第'+str(i+1)+'组')
    ax1.legend(loc="best")
    ax1.set_title(title,fontsize=16)
    xt = np.arange(0,int(len(datelist)/10)*10,int(len(datelist)/100)*4)
    xtick = [datelist[x] for x in xt]
    ax1.set_xticks(xtick)
    plt.xticks(rotation = 45)
    plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)
    plt.legend(fontsize = 15)
    return fig1


#%%
if __name__ == '__main__':
    plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
    plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
    
    fig1 = plot_PnL_Df(Dfprofit,DfAll,title = '市值——PnL')
    fig1.savefig('temp.png')
