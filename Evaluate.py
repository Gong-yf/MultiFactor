# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 11:39:12 2019

@author: yifan.gong
"""
import sys
sys.path.append("C:\\Users\yifan.gong\Documents\PythonWorkspace\privatelibs")

import pandas as pd
import numpy as np
from TradeModule.PoolBasic import GetPoolBasic
from TradeModule.FactorRank import GetFactorRank
from TradeModule.datadaily import GetDatadaily
from TradeModule.datamapping import GetDatamapping
import datetime
from TradingCalendar.Tradedate import GetTradedate
from TradingCalendar.monthlyseries import MonthlySeries

from matplotlib import pyplot as plt

class Evaluate_factor(object):
    def __init__(self,startdate,enddate,Open,close,
                 pre_close,adjfactor,mkt_cap_float,
                 delist,suspend,maxupordown,ipo_date,**kw):
        self.startdate = startdate
        self.enddate = enddate
        self.Open = Open
        self.close = close
        self.pre_close = pre_close
        self.adjfactor = adjfactor
        self.mkt_cap_float = mkt_cap_float
        self.delist = delist
        self.suspend = suspend
        self.maxupordown = maxupordown
        self.ipo_date = ipo_date
        pool = Open.index.intersection(
                close.index.intersection(
                        pre_close.index.intersection(
                                adjfactor.index.intersection(
                                        mkt_cap_float.index.intersection(
                                                        suspend.index.intersection(
                                                                maxupordown.index.intersection(
                                                                        ipo_date.index)))))))
        self.pool = pool
        self.kw = kw
        self.key = list(kw.keys())[0]
    
    def find(self,value,sindex):
        for v in sindex:
            if value<=v:
                return v
        
    def Csum(self):
        startdate = self.startdate
        enddate = self.enddate
        Open = self.Open
        close = self.close
        pre_close = self.pre_close
        adjfactor = self.adjfactor
        mkt_cap_float = self.mkt_cap_float
        delist = self.delist
        suspend = self.suspend
        maxupordown = self.maxupordown
        ipo_date = self.ipo_date
        pool = self.pool
        kw = self.kw
        
        
        datelist = GetTradedate()[:]
        datelist = [v for v in datelist if v>=startdate and v<=enddate]
        m = MonthlySeries(datelist)
        monthend = m.month_end()
        
        Cumsum = pd.DataFrame(columns = ['factor_rank','pct_chg_ex'])
        Cindex = [i/4000 for i in range(4000)]
        
        for i in range(1,len(monthend)):
            #在月末，对因子排序
            date1 = monthend[i-1]
            datadaily1 = GetDatadaily(date1,pool,Open,close,pre_close,adjfactor,mkt_cap_float,**kw)
            datamapping = GetDatamapping(date1,pool,delist,suspend,maxupordown,ipo_date)
            poolbasic = GetPoolBasic(datadaily1,datamapping,date1)
            poolrank = GetFactorRank(datadaily1,poolbasic,by = self.key)
            
            date0 = monthend[i]
            print('\033[31;47;1m交易日期：'+date0+'\033[0m')
            t1 = datetime.datetime.now()
            datadaily = GetDatadaily(date0,pool,Open,close,pre_close,adjfactor,mkt_cap_float,**kw)
            datamapping = GetDatamapping(date0,pool,delist,suspend,maxupordown,ipo_date)   
            poolbasic = GetPoolBasic(datadaily,datamapping,date0)
            indext = poolrank.index.intersection(poolbasic)
            poolrank = poolrank.loc[indext,:]
            poolrank.loc[:,'factor_rank'] = [i/len(indext) for i in range(len(indext))]
            v = datadaily.loc[indext,'close']*datadaily.loc[indext,'adjfactor']
            prev = datadaily1.loc[indext,'close']*datadaily1.loc[indext,'adjfactor']
            poolrank.loc[indext,'pct_chg'] =  v/prev-1
    
            
            temp = poolrank.describe()
            poolrank.loc[:,'pct_chg_ex'] = poolrank.loc[:,'pct_chg'] - temp.loc['mean','pct_chg']
            
            tindex = poolrank.loc[:,'factor_rank'].apply(lambda x:self.find(x,Cindex))
            poolrank.loc[:,'factor_rank'] = tindex.values   
            poolcs = pd.DataFrame(data = poolrank.loc[:,['factor_rank','pct_chg_ex']].values,columns = ['factor_rank','pct_chg_ex'])
            Cumsum = pd.concat([Cumsum,poolcs])
    
            t7 = datetime.datetime.now()
            print('\033[31m当天使用时间：'+str(t7-t1)+'\033[0m')
        Cs = Cumsum.groupby('factor_rank').sum().cumsum()
        
        fig1 = plt.figure(figsize = (16,9),dpi = 200)
        ax1 = fig1.add_subplot(111)
        ax1.plot(np.arange(0,1,1/len(Cs)),Cs)
        
        return Cumsum,Cs,fig1
    
    def rankIC(self):
        startdate = self.startdate
        enddate = self.enddate
        Open = self.Open
        close = self.close
        pre_close = self.pre_close
        adjfactor = self.adjfactor
        mkt_cap_float = self.mkt_cap_float
        kw = self.kw
        delist = self.delist
        suspend = self.suspend
        maxupordown = self.maxupordown
        ipo_date = self.ipo_date
        pool = self.pool
              
        datelist = GetTradedate()[:]
        datelist = [v for v in datelist if v>=startdate and v<=enddate]
        m = MonthlySeries(datelist)
        monthend = m.month_end()
        
        rankIC = {}
        
        for i in range(1,len(monthend)):
            #在月末，对因子排序
            date1 = monthend[i-1]
            datadaily1 = GetDatadaily(date1,pool,Open,close,pre_close,adjfactor,mkt_cap_float,**kw)
            datamapping = GetDatamapping(date1,pool,delist,suspend,maxupordown,ipo_date)
            poolbasic = GetPoolBasic(datadaily1,datamapping,date1)
            poolrank = GetFactorRank(datadaily1,poolbasic,by = self.key)
            
            date0 = monthend[i]
            print('\033[31;47;1m交易日期：'+date0+'\033[0m')
            t1 = datetime.datetime.now()
            datadaily = GetDatadaily(date0,pool,Open,close,pre_close,adjfactor,mkt_cap_float,**kw)
            datamapping = GetDatamapping(date0,pool,delist,suspend,maxupordown,ipo_date)   
            poolbasic = GetPoolBasic(datadaily,datamapping,date0)
            indext = poolrank.index.intersection(poolbasic)
            poolrank = poolrank.loc[indext,:]
            poolrank.loc[:,'factor_rank'] = [i/len(indext) for i in range(len(indext))]
            v = datadaily.loc[indext,'close']*datadaily.loc[indext,'adjfactor']
            prev = datadaily1.loc[indext,'close']*datadaily1.loc[indext,'adjfactor']
            poolrank.loc[indext,'pct_chg'] =  v/prev-1
           
            temp = poolrank.describe()
            poolrank.loc[:,'pct_chg_ex'] = poolrank.loc[:,'pct_chg'] - temp.loc['mean','pct_chg']
            poolrank = poolrank.sort_values(by = ['pct_chg_ex'])
            poolrank.loc[:,'pct_chg_ex'] = [i/len(indext) for i in range(len(indext))]
            
            ICtemp = np.corrcoef(poolrank.loc[:,'pct_chg_ex'],poolrank.loc[:,'factor_rank'])[0,1]
            rankIC[date0] = ICtemp
    
            t7 = datetime.datetime.now()
            print('\033[31m当天使用时间：'+str(t7-t1)+'\033[0m')
            
        fig1 = plt.figure(figsize = (16,9),dpi = 200)
        ax1 = fig1.add_subplot(111)
        ax1.bar(rankIC.keys(),rankIC.values())
        xt = np.arange(0,int(len(rankIC.keys())/2)*2,int(len(rankIC.keys())/10))
        xtick = [list(rankIC.keys())[x] for x in xt]
        ax1.set_xticks(xtick)
        plt.xticks(rotation = 45)
    
        return rankIC,fig1
    
    def IC(self):
        startdate = self.startdate
        enddate = self.enddate
        Open = self.Open
        close = self.close
        pre_close = self.pre_close
        adjfactor = self.adjfactor
        mkt_cap_float = self.mkt_cap_float
        kw = self.kw
        delist = self.delist
        suspend = self.suspend
        maxupordown = self.maxupordown
        ipo_date = self.ipo_date
        pool = self.pool
              
        datelist = GetTradedate()[:]
        datelist = [v for v in datelist if v>=startdate and v<=enddate]
        m = MonthlySeries(datelist)
        monthend = m.month_end()
        
        IC = {}
        
        for i in range(1,len(monthend)):
            #在月末，对因子排序
            date1 = monthend[i-1]
            datadaily1 = GetDatadaily(date1,pool,Open,close,pre_close,adjfactor,mkt_cap_float,**kw)
            datamapping = GetDatamapping(date1,pool,delist,suspend,maxupordown,ipo_date)
            poolbasic = GetPoolBasic(datadaily1,datamapping,date1)
            poolrank = GetFactorRank(datadaily1,poolbasic,by = self.key)
            
            date0 = monthend[i]
            print('\033[31;47;1m交易日期：'+date0+'\033[0m')
            t1 = datetime.datetime.now()
            datadaily = GetDatadaily(date0,pool,Open,close,pre_close,adjfactor,mkt_cap_float,**kw)
            datamapping = GetDatamapping(date0,pool,delist,suspend,maxupordown,ipo_date)   
            poolbasic = GetPoolBasic(datadaily,datamapping,date0)
            indext = poolrank.index.intersection(poolbasic)
            poolrank = poolrank.loc[indext,:]
            v = datadaily.loc[indext,'close']*datadaily.loc[indext,'adjfactor']
            prev = datadaily1.loc[indext,'close']*datadaily1.loc[indext,'adjfactor']
            poolrank.loc[indext,'pct_chg'] =  v/prev-1
           
            temp = poolrank.describe()
            poolrank.loc[:,'pct_chg_ex'] = poolrank.loc[:,'pct_chg'] - temp.loc['mean','pct_chg']
            
            ICtemp = np.corrcoef(poolrank.loc[:,'pct_chg_ex'],poolrank.loc[:,self.key])[0,1]
            IC[date0] = ICtemp
    
            t7 = datetime.datetime.now()
            print('\033[31m当天使用时间：'+str(t7-t1)+'\033[0m')
            
        fig1 = plt.figure(figsize = (16,9),dpi = 200)
        ax1 = fig1.add_subplot(111)
        ax1.bar(IC.keys(),IC.values())
        xt = np.arange(0,int(len(IC.keys())/2)*2,int(len(IC.keys())/10))
        xtick = [list(rankIC.keys())[x] for x in xt]
        ax1.set_xticks(xtick)
        plt.xticks(rotation = 45)
    
        return IC,fig1

class Evaluate_portfolio(object):
    def __init__(self,DfAll):
        self.DfAll = DfAll
        self.datelist = list(DfAll.keys())
        
    def annualized_return(self,Df):
        start = datetime.datetime.strptime(self.datelist[0],'%Y%m%d')
        end = datetime.datetime.strptime(self.datelist[-1],'%Y%m%d')
        timel = (end-start).days
        Asset1 = Df[self.datelist[0]]['Asset']
        Asset2 = Df[self.datelist[-1]]['Asset']
        annulrtn = np.exp(365/timel*np.log(Asset2/Asset1))-1
        return annulrtn    
    
    def annualized_return_excess(self,Df):
        annulrtn = self.annualized_return(Df)
        annulrtn_b = self.annualized_return(self.DfAll)
        return annulrtn-annulrtn_b
        
    def information_ratio(self,Df):
        rtn = [Df[date0]['Assetpct']-self.DfAll[date0]['Assetpct'] for date0 in self.datelist]
        IR = np.mean(rtn)/np.std(rtn)
        return IR
        
    def maxdrawdown(self,Df):
        Asset = [Df[date0]['Asset'] for date0 in self.datelist]
        flag = Asset[0]
        bottom = Asset[0]
        drawdown = [0]
        d = 0
        for v in Asset:
            if v>=flag:
                flag = v
                bottom = v
                drawdown.append(d)
            elif v<=bottom:
                bottom = v
                d = (bottom-flag)/flag
        drawdown.append(d)
        maxdrawdown = -min(drawdown)
        return maxdrawdown

#%%
if __name__ == '__main__':
    startdate = '20130304'
    enddate = '20180105'
    kw = {'factor_profit':factor_profit}
    e = Evaluate_factor(startdate,enddate,Open,close,
                 pre_close,adjfactor,mkt_cap_float,
                 delist,suspend,maxupordown,ipo_date,**kw)
    
    rankIC,fig_rIC = e.rankIC()
    fig_rIC.savefig('temprankIC.png')
    
    IC,fig_IC = e.IC()
    fig_IC.savefig('tempIC.png')
    
    Cumsum,Cs,fig_cumsum = e.Csum()
    fig_cumsum.savefig('Cumsumtemp.png')
    #%%
    Dfprofit = load_obj('C:\\Users\yifan.gong\Documents\PythonWorkspace\FinanceStatement\\Df_profit_v4.pkl')
    DfAll = load_obj('C:\\Users\yifan.gong\Documents\PythonWorkspace\FinanceStatement\\DfAll_profit_v4.pkl')
    ep = Evaluate_portfolio(DfAll)
    n =10
    ev = pd.DataFrame(index = ['全市场']+['第'+str(i+1)+'组' for i in range(n)],
                      columns = ['年化收益率','年化超额收益','IR','最大回撤'])
    ev.iloc[0,0] = ep.annualized_return(DfAll)
    ev.iloc[0,1] = ep.annualized_return_excess(DfAll)
    ev.iloc[0,2] = ep.information_ratio(DfAll)
    ev.iloc[0,3] = ep.maxdrawdown(DfAll)
    for i in range(n):
        ev.iloc[i+1,0] = ep.annualized_return(Dfprofit[i])
        ev.iloc[i+1,1] = ep.annualized_return_excess(Dfprofit[i])
        ev.iloc[i+1,2] = ep.information_ratio(Dfprofit[i])
        ev.iloc[i+1,3] = ep.maxdrawdown(Dfprofit[i])
    ev.to_csv('Evaluate_profityoy.csv',encoding = 'utf8')
