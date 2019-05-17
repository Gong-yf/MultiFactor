# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 14:15:05 2019

@author: yifan.gong
"""
import numpy as np
from copy import deepcopy

class LinearRegress(object):
    def __init__(self,X:np.matrix,Y:np.matrix):
        self.__rowX = X.shape[0]
        self.X = np.c_[np.ones(self.__rowX),X]
        self.__colX = self.X.shape[1]
        self.Y = Y if Y.shape[0] == X.shape[0] else Y.T
        if self.Y.shape[0] != self.X.shape[0]:
            raise ValueError("The row_num of X and Y must match.")
#            print('\033[31;1mInvalid Input:\033[0m The row_num of X and Y must match.')
    
    def OLS(self):
        result = np.dot(np.asmatrix(np.dot(self.X.T,self.X)).I,np.dot(self.X.T,self.Y))
        alpha = np.asarray(result[0])
        beta = np.asarray(result[1:])
        Y_predict = np.dot(self.X,result)
        epi = np.asarray(self.Y-Y_predict)
        return alpha,beta,epi
    
    def __phi__(self,k):
        k = abs(k)
        def phi(x):
            if x>k:
                return k
            elif x< -k:
                return -k
            else:
                return x
        return phi
    
    def __W__(self,u,k):
        u = u.reshape(1,-1)[0]
        phi = self.__phi__(k)
        v = [phi(val)/val if val != 0 else 0 for val in u]
        W = np.diag(v)
        return W
    
    def Mestimator(self):
        alpha,beta,epi = self.OLS()
        beta1 = np.r_[alpha,beta]
        beta0 = np.ones(self.__colX).reshape(-1,1)
        k = np.mean(epi)
        while(max(abs(beta1-beta0))>0.00001):
            beta0 = deepcopy(beta1)
            try:
                u = 0.5*epi/np.sqrt(np.median(epi)**2+(k)**2)
            except ValueError:
                return alpha,beta,epi
            W = self.__W__(u,k)
            temp1 = np.dot(self.X.T,np.dot(W,self.X))
            temp2 = np.dot(self.X.T,np.dot(W,self.Y))
            result = np.dot(temp1.I,temp2)
            alpha = np.asarray(result[0])
            beta = np.asarray(result[1:])
            Y_predict = np.dot(self.X,result)
            epi = np.asarray(self.Y-Y_predict)
            beta1 = np.r_[alpha,beta]
        
        return alpha,beta,epi
  #%%  
if __name__ == '__main__':
    import random
    from matplotlib import pyplot as plt
    import datetime
    
    t1 = datetime.datetime.now()
    
    X1 = [random.random()*10 for i in range(500)]
    Y1 = [random.uniform(7,12)*val+random.uniform(-10,10) for val in X1]
    X2 = [random.random()*10 for i in range(50)]
    Y2 = [random.uniform(7,12)*val+random.uniform(0,1000) for val in X2]
    X = X1+X2
    Y = Y1+Y2
#    X = np.asmatrix(an.iloc[2:,2]).tolist()[0]
#    Y = np.asmatrix(an.iloc[2:,0]).tolist()[0]
    
    fig1 = plt.figure(figsize = (2,6),dpi = 200)
    ax0 = fig1.add_subplot(311)
    ax0.scatter(X,Y,edgecolor='none',s = 5)
    
    l = LinearRegress(np.mat(X).reshape(-1,1),np.mat(Y))
    
    alpha1,beta1,epi1 = l.OLS()
    Y_predict1 = beta1*X+alpha1 
    
    ax1 = fig1.add_subplot(312)
    ax1.scatter(X,Y,edgecolor='none',s = 5)
    ax1.plot(X,Y_predict1[0],c = 'r',linewidth = 0.5)
    
    alpha2,beta2,epi2 = l.Mestimator()
    Y_predict2 = beta2*X+alpha2
    
    ax2 = fig1.add_subplot(313)
    ax2.scatter(X,Y,edgecolor='none',s = 5)
    ax2.plot(X,Y_predict2[0],c = 'r',linewidth = 0.5)
    
    print(str(datetime.datetime.now()-t1))