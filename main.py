# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 09:45:53 2019

@author: yifan.gong
"""

import sys
sys.path.append("C:\\Users\yifan.gong\Documents\PythonWorkspace\privatelibs")

import pandas as pd
import datetime
from TradingCalendar.Tradedate import GetTradedate

class Trade(object):
    def __init__(self,startdate,enddate,Open,close,pre_close,pct_chg,adjfactor,mkt_cap_float,
             delist,suspend,maxupordown,timedelta_ipo):
        self.startdate = startdate
        self.enddate = enddate
        pool = Open.index.intersection(
            close.index.intersection(
                    pre_close.index.intersection(
                            adjfactor.index.intersection(
                                    mkt_cap_float.index.intersection(
                                                    suspend.index.intersection(
                                                            maxupordown.index.intersection(
                                                                    timedelta_ipo.index)))))))
        pool = pool.drop_duplicates(keep='first')
        self.pool = pool
        self.Open = Open.reindex(pool)
        self.close = close.reindex(pool)
        self.pre_close = pre_close.reindex(pool)
        self.pct_chg = pct_chg.reindex(pool)
        self.adjfactor = adjfactor.reindex(pool)
        self.mkt_cap_float = mkt_cap_float.reindex(pool)
        self.delist = delist.reindex(pool)
        self.suspend = suspend.reindex(pool)
        self.maxupordown = maxupordown.reindex(pool)
        self.timedelta_ipo = timedelta_ipo.reindex(pool)
    
    def GetDatadaily(self,date0):
        datadaily = pd.DataFrame(index = self.pool)
        datadaily.loc[:,'Open'] = self.Open.loc[:,date0]
        datadaily.loc[:,'close'] = self.close.loc[:,date0]
        datadaily.loc[:,'pre_close'] = self.pre_close.loc[:,date0]
        datadaily.loc[:,'pct_chg'] = self.pct_chg.loc[:,date0]
        datadaily.loc[:,'adjfactor'] = self.adjfactor.loc[:,date0]
        datadaily.loc[:,'mkt_cap_float'] = self.mkt_cap_float.loc[:,date0]

        return datadaily
    
    def GetDatamapping(self,date0):
        datamapping = pd.DataFrame(index = self.pool)
        datamapping.loc[:,'delist'] = self.delist.loc[:,date0].fillna(0)
        datamapping.loc[:,'suspend'] = self.suspend.loc[:,date0].fillna(1)
        datamapping.loc[:,'maxupordown'] = self.maxupordown.loc[:,date0].fillna(1)
        datamapping.loc[:,'timedelta_ipo'] = self.timedelta_ipo.loc[:,date0].fillna(0)
        
        return datamapping

    def GetPoolBasic(self,date0,datadaily):
        datamapping = self.GetDatamapping(date0)
        poolmapping = datamapping[(datamapping.loc[:,'delist'] != True)& #删除退市列表
                                  (datamapping.loc[:,'suspend'] != True)& #删除停牌
                                  (datamapping.loc[:,'maxupordown'] != True)&#删除涨跌停
                                  (datamapping.loc[:,'timedelta_ipo']>183)]        
        poolmapping = poolmapping.index
        poolbasic = datadaily.dropna().index.intersection(poolmapping)
        
        return poolbasic
    
    def GetFactorRank(self,date0,poolbasic,factor):
        factor = factor.loc[poolbasic,date0]
        poolrank = factor.sort_values().dropna()
        return poolrank
    
    def GetPoolPrepBuy(self,datadaily,poolbasic,poolrank,rank = (0,0.2)):
        if rank[0]<0 or rank[1]>1 or rank[0]>=rank[1]:
            print('\033[1;31m rank range error:must be a range between 0 and 1')
            return
        pool = poolrank.index.intersection(poolbasic)
        poolprepbuy = pd.DataFrame(index = poolrank.loc[pool].index)
        poolprepbuy.loc[:,'Open'] = datadaily.loc[pool,'Open']
        poolprepbuy.loc[:,'close'] = datadaily.loc[pool,'close']
        poolprepbuy.loc[:,'pre_close'] = datadaily.loc[pool,'pre_close']
        poolprepbuy.loc[:,'pct_chg'] = datadaily.loc[pool,'pct_chg']
        poolprepbuy.loc[:,'mkt_cap_float'] = datadaily.loc[pool,'mkt_cap_float']
        poolprepbuy = poolprepbuy.dropna()
        
        bb = int(rank[0]*len(pool))
        up = int(rank[1]*len(pool))
        
        poolindex = poolprepbuy.iloc[bb:up]
        
        return poolindex

    def GetSellExec(self,datadaily,stockholding,cashholding,poolbasic,poolprepbuy):        
        SellToday = pd.DataFrame(columns = ['Volume','Price','adjfactor'])
        Selllist = [stock for stock in stockholding.index if stock in poolbasic and stock not in poolprepbuy.index]
        if Selllist == []:
            return SellToday,stockholding,cashholding
        SellToday.loc[:,'adjfactor'] = datadaily.loc[Selllist,'adjfactor']/stockholding.loc[Selllist,'adjfactor']
        SellToday.loc[:,'Price'] = datadaily.loc[Selllist,'Open']
        SellToday.loc[:,'Volume'] = stockholding.loc[Selllist,'Volume']
        cashholding += sum(SellToday.loc[:,'Price'] * SellToday.loc[:,'Volume']*SellToday.loc[:,'adjfactor'])
        stockholding = stockholding.drop(index = Selllist)
        return SellToday,stockholding,cashholding
    
    def GetBuyExec(self,datadaily,stockholding,cashholding,poolprepbuy,weight = 'equal'):
        Buylist = []
        #更新今日买入名单。对计划买入的股票，如果已在持仓，则不买入
        Buylist = [stock for stock in poolprepbuy.index if stock not in stockholding.index]
        BuyToday = {}
        if Buylist ==[]:
            return BuyToday,stockholding,cashholding
        BuyNum = len(Buylist)
        if weight == 'equal':
            BuyValue = int(cashholding/BuyNum) 
            for stock in Buylist:
                BuyToday[stock] = {}
                price = poolprepbuy.loc[stock,'Open']
                vol = int(BuyValue/(100*price))*100
                cashholding -= price*vol
                BuyToday[stock]['Price'] = price
                BuyToday[stock]['Volume'] = vol
            stockholding = pd.concat([stockholding,pd.DataFrame(BuyToday).T],sort=False)
            stockholding.loc[Buylist,'adjfactor'] = datadaily.loc[Buylist,'adjfactor']
        elif weight == 'mkt_cap_float':
            tot = sum(poolprepbuy.loc[Buylist,'mkt_cap_float'])
            for stock in Buylist:
                BuyToday[stock] = {}
                BuyValue = cashholding*poolprepbuy.loc[stock,'mkt_cap_float']/tot
                price = poolprepbuy.loc[stock,'Open']
                vol = int(BuyValue/(100*price))*100
                cashholding -= price*vol
                BuyToday[stock]['Price'] = price
                BuyToday[stock]['Volume'] = vol
            stockholding = pd.concat([stockholding,pd.DataFrame(BuyToday).T],sort=False)
            stockholding.loc[Buylist,'adjfactor'] = datadaily.loc[Buylist,'adjfactor']
        
        return BuyToday,stockholding,cashholding
    
    def BackTest(self,factor,asset = 100000000,rank = (0,0.2),weight = 'equal'):
        datelist = GetTradedate()[:]
        datelist = [v for v in datelist if v>=self.startdate and v<=self.enddate]
        daterank = datelist[:-1]
        datetrade = datelist[1:]
    
        stockholding = pd.DataFrame(columns = ['Volume','Price','close','adjfactor','adjfactorlatest'])
        Asset = asset
        Assetpre = asset
        cashholding = asset
        Df = {}
        t0 = datetime.datetime.now()
        print('开始时间：'+str(t0))
        
        datadaily = self.GetDatadaily(daterank[0]) 
        poolbasic = self.GetPoolBasic(daterank[0],datadaily)
        poolrank = self.GetFactorRank(daterank[0],poolbasic,factor)
        
        for i,date0 in enumerate(datetrade):
#            date1 = daterank[i]
            print('\033[31;47;1m交易日期：'+date0+'\033[0m')
            t2 = datetime.datetime.now()
            
            datadaily = self.GetDatadaily(date0)
            poolbasic = self.GetPoolBasic(date0,datadaily)             
            poolprepbuy = self.GetPoolPrepBuy(datadaily,poolbasic,poolrank,rank = rank) 
            
            SellToday,stockholding,cashholding = self.GetSellExec(datadaily,stockholding,cashholding,poolbasic,poolprepbuy)
            BuyToday,stockholding,cashholding = self.GetBuyExec(datadaily,stockholding,cashholding,poolprepbuy,weight = weight)
            
            poolrank = self.GetFactorRank(date0,poolbasic,factor)

                        
            sindex = stockholding.index.intersection(self.delist.loc[:,date0][self.delist.loc[:,date0]==0].index)
            stockholding = stockholding.reindex(sindex)
            stockholding.loc[:,'adjfactorlatest'] = datadaily.loc[:,'adjfactor']
            stockholding.loc[:,'close'] = datadaily.loc[stockholding.index,'close']
            stockholding = stockholding.fillna(method = 'ffill', axis = 1)
            Asset = cashholding + sum(stockholding.loc[:,'Volume']*stockholding.loc[:,'close']*stockholding.loc[:,'adjfactorlatest']/stockholding.loc[:,'adjfactor'])
            Assetpct = Asset/Assetpre-1
            Assetpre = Asset
            Df[date0] = {'Asset':Asset,'Assetpct':Assetpct,'cashholding':cashholding,'Buy':BuyToday,
              'stockholding':stockholding.to_dict(),'Sell':SellToday.to_dict(),'SelectStock':poolprepbuy.to_dict()}  
#            print('Df:'+str(datetime.datetime.now()-t1))
            
            t7 = datetime.datetime.now()
            print('\033[31m当天使用时间：'+str(t7-t2)+'\033[0m')
        t8 = datetime.datetime.now()
        print('\033[31m运行时间：'+str(t8-t0)+'\033[0m')
        return Df
#%%    
if __name__ == '__main__':
    import sys
    sys.path.append("C:\\Users\yifan.gong\Documents\PythonWorkspace\privatelibs")

    from set_col import set_col
    from dictfile import save_obj,load_obj   
    path = 'C:\\Users\yifan.gong\Documents\PythonWorkspace\data\\'
    #%%
    Open = pd.read_csv(path+'open.csv',index_col = 0).T
    close = pd.read_csv(path+'close.csv',index_col = 0).T
    pre_close = pd.read_csv(path+'pre_close.csv',index_col = 0).T
    adjfactor = pd.read_csv(path+'adjfactor.csv',index_col = 0).T
    maxupordown = pd.read_csv(path+'maxupordown.csv',index_col = 0).T
    suspend = pd.read_csv(path+'suspend.csv',index_col = 0).T
    timedelta_ipo = pd.read_csv(path+'timedelta_ipo.csv',index_col = 0).T
    mkt_cap_float  = pd.read_csv(path+'mkt_cap_float.csv',index_col = 0).T
    delist = pd.read_csv(path+'delist.csv',index_col = 0).T
    pct_chg = pd.read_csv(path+'pct_chg.csv',index_col = 0).T
    set_col(pct_chg)
    set_col(delist)
    set_col(mkt_cap_float)
    set_col(Open)
    set_col(close)
    set_col(pre_close)
    set_col(adjfactor)
    set_col(maxupordown)
    set_col(suspend)
    set_col(timedelta_ipo)
    
#    SWIndustry_cross = load_obj(path+'SWIndustry_cross.pkl')
#    SWIndustry_timeseries = load_obj(path+'SWIndustry_timeseries.pkl')
    
    mkt_cap_ard = pd.read_csv(path+'mkt_cap_ard.csv',index_col = 0).T
    set_col(mkt_cap_ard)
    #%%
    startdate = '20130104'
    enddate = '20180705'
    t = Trade(startdate,enddate,Open,close,pre_close,pct_chg,adjfactor,mkt_cap_float,
             delist,suspend,maxupordown,timedelta_ipo)
    n = 5
    Dfprofit = [0 for i in range(n)]
    for i in range(n):
        Dfprofit[i] = t.BackTest(mkt_cap_ard,asset = 100000000,rank = (i/n,i/n+1/n),weight = 'equal')
    save_obj(Dfprofit,'Df_mkt_v1.pkl')
    
    
    DfAll = t.BackTest(mkt_cap_ard,asset = 100000000,rank = (0,1),weight = 'equal')
    save_obj(DfAll,'DfAll_mkt_v1.pkl')
