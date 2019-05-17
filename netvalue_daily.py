# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 15:01:22 2019

@author: yifan.gong
"""

def netvalue_daily(startdate,enddate,datelist,Df,close,adjfactor):
    date_monthly = list(Df.keys())
    datelist = [v for v in datelist if v>=startdate and v<=enddate]
    datelist = [v for v in datelist if v >= date_monthly[0] and v <= date_monthly[-1]]
    netvalue = {}
    i = 0
    dateb = date_monthly[i]
    datee = date_monthly[i+1]
    for date0 in datelist:
        if date0 >= datee:
            i = i+1
            dateb = date_monthly[i]
            if datee != date_monthly[-1]:
                datee = date_monthly[i+1]
        stockholding = Df[dateb]['stockholding']
        cashholding = Df[dateb]['cashholding']
        stockholding.loc[:,'adjfactorlatest'] = adjfactor.loc[stockholding.index,date0]
        stockholding.loc[:,'close'] = close.loc[stockholding.index,date0]
        stockholding = stockholding.fillna(method = 'ffill', axis = 1)
        netvalue[date0] = cashholding + sum(
                stockholding.loc[:,'Volume']*stockholding.loc[:,'close']*
                stockholding.loc[:,'adjfactorlatest']/stockholding.loc[:,'adjfactor'])
    
    return netvalue
#%%
if __name__ == '__main__':
    from TradingCalendar.Tradedate import GetTradedate
    datelist = GetTradedate()[:]
    path = 'C:\\Users\yifan.gong\Documents\PythonWorkspace\data\\'
    close = pd.read_csv(path+'close.csv',index_col = 0).T
    adjfactor = pd.read_csv(path+'adjfactor.csv',index_col = 0).T
    set_col(close)
    set_col(adjfactor)
    n = 10
    NVprofit = [0 for i in range(n)]
    for i in range(n):
        NVprofit[i] = netvalue_daily(startdate,enddate,datelist,Dfprofit[i],close,adjfactor)
#    DfAll = load_obj('DfAll_profit.pkl')
    NVAll = netvalue_daily(startdate,enddate,datelist,DfAll,close,adjfactor)
