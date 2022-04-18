import numpy as np
import pandas as pd
"""
inputs: 
        - data:             coefficient of the variable                 ==> numpy.ndarray
        - sts:              the result of every equation                ==> numpy.ndarray
        - z:                coefficient of the z equation               ==> list 
        - situations:       the situation of every equation(=,<=,>=)    ==> list
        - columns:          the names of the variables                  ==> list 
        - M = 1000                                                      ==> 
        - isMax==True :     the situation of z(max or min)              ==> boolean
        - iteration=100 :   max iteration value                         ==>
"""
class SimpleksMM():
    def __init__(self,data,sts,z,situations,columns,M=1000,isMax=True,iteration=100):
        self.data = data
        self.sts = np.array(sts , dtype = "float").reshape(sts.shape[0],1)
        self.z = z
        self.situations = situations
        self.columns = columns
        self.M = M
        self.isMax = isMax
        self.iteration = iteration
        self.cj = np.zeros((self.data.shape[0],1))
        
        self.cj_name = []
        
        self.__MControl()
        self.__add()
    def solve(self):
        _iteration = 0
        while (True):
            zj = (self.cj * self.data).sum(axis = 0)
            z = np.array(self.z)
            cj_zj = z - zj
            self.answer = (self.cj * self.sts).sum()
            
            #sellecting the min or max column according to Zmin - Zmax
            if(self.isMax):
                _minMax = cj_zj.argmax()
            else: _minMax = cj_zj.argmin()
                
            #finishing the loop
            if (self.isMax and cj_zj[_minMax] <= 0):
                break
            elif (self.isMax == False and cj_zj[_minMax] >= 0):
                break
            #reached the max iteration
            elif (self.iteration == _iteration):
                break
            
            #when the sellected column has 0
            if(0 in self.data[:,_minMax]):
                _nWhere = np.where(self.data[:,_minMax] != 0)[0]
                _values = self.data[:,_minMax][_nWhere]
                rate = (self.sts[_nWhere]).reshape(_nWhere.shape[0],1) / (_values).reshape(_values.shape[0],1)              
            else: rate = self.sts / (self.data[:,_minMax]).reshape(self.data.shape[0],1)
            
            #if the rate has negative value, the value will change
            while(True):
                if(rate.min() > 0):
                    break
                rate[rate.argmin()] = 99999

            _point = ( rate.argmin() , _minMax)

            self.__change(_point)
            
            _iteration += 1
    
    def __change(self,point):
        #changing root row
        value = self.data[point[0],point[1]]
        self.data[point[0],:] = self.data[point[0],:] / value
        self.sts[point[0],:] = self.sts[point[0],:] / value
        
        #changing the data according to root row
        for i in range(self.data.shape[0]):
            if(i == point[0]): continue
            value = -self.data[i,point[1]]
            self.data[i,:] = value * self.data[point[0],:] + self.data[i,:]
            self.sts[i,:] = value * self.sts[point[0],:] + self.sts[i,:]
        
        #changing cj and cj_name
        self.cj[point[0]] = self.z[point[1]]
        self.cj_name[point[0]] = self.columns[point[1]]
    
    def __add(self):
        for i in range(len(self.situations)):
            zero = np.zeros((self.data.shape[0],1))
            if self.situations[i] == "<=":
                #data
                zero[i] = 1
                self.data = np.concatenate([self.data,zero],axis = 1)
                
                #z and z'name
                _name = "S"+str(i+1)
                self.columns.append(_name)
                self.z.append(0)
                
                #cj and cj_name
                self.cj_name.append(_name)
                #self.cj[i,1] = 0 is not necessary
                
            elif self.situations[i] == ">=":
                #data
                _zero = zero.copy()
                zero[i] = -1
                _zero[i] = 1
                self.data = np.concatenate([self.data,zero],axis = 1)
                self.data = np.concatenate([self.data,_zero],axis = 1)
                
                #z and z'name
                _name = "S"+str(i+1)
                self.z.append(0)
                self.columns.append(_name)
                _name = "A"+str(i+1)
                self.z.append(self.M)
                self.columns.append(_name)
                
                #cj and cj_name
                self.cj_name.append(_name)
                self.cj[i] = self.M
                
            elif self.situations[i] == "=":
                #data
                zero[i] = 1
                self.data = np.concatenate([self.data,zero],axis = 1)
                
                #z and z'name
                _name = "A"+str(i+1)
                self.columns.append(_name)
                self.z.append(self.M)
                
                #cj and cj_name
                self.cj_name.append(_name)
                self.cj[i] = self.M
                

    def show(self):
        return {"data":self.data,
                "z":self.z,
                "columns":self.columns,
                "cj":self.cj,
                "cj_name":self.cj_name,
                "answer":self.answer,
                "sts":self.sts}

    def __MControl(self):
        if(self.isMax):
            if(self.M > 0): self.M *= -1
        else:
            if(self.M < 0): self.M *= -1
            
    def table(self):
        l_data = pd.DataFrame(self.cj , columns=["cj"] , index=self.cj_name)
        l_data[self.columns] = self.data
        l_data["STS"] = self.sts
        return l_data
        
        