



import math
import pandas as pd
import numpy as np
import warnings
from arch import unitroot
from sklearn.base import BaseEstimator,TransformerMixin
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scientisttseries.utils import lag, diff, extractAIC,extractAICC,extractBIC, residuals


class DF(BaseEstimator,TransformerMixin):
    """Dickey Fuller Test

    Parameters
    ---------
    y : {ndarray, Series}
        The data to test for a unit root
    typ : {'none','drift','trend'}, optional
        The trend component to include in the test

        - "none" - No trend components (Default)
        - "drift" - Include a constant
        - "trend" - Include a constant and linear time trend
    
    Notes
    -----
    The null hypothesis of the Dickey-Fuller is that there is a unit
    root, with the alternative that there is no unit root. If the pvalue is
    above a critical size, then the null cannot be rejected that there
    and the series appears to be a unit root.

    The p-values are obtained through regression surface approximation from
    MacKinnon (1994) using the updated 2010 tables.
    If the p-value is close to significant, then the critical values should be
    used to judge whether to reject the null.
    """
    def __init__(self,y,typ):
        
        y = np.array(y)
        data = pd.DataFrame(y,columns=["y"])

        #####################################################################
        # Dickey - Fuller Unit root test
        ####################################################################

        if typ == "none":
            lm = smf.ols(formula="y~lag(y,1)-1",data=data).fit()
            tau1 = (lm.params[0]-1)/np.sqrt(lm.cov_params().iloc[0,0])
            teststat = pd.DataFrame({"tau1" : tau1},index=["statistic"])
        elif typ == "drift":
            lm = smf.ols(formula="y~lag(y,1)",data=data).fit()
            tau2 = (lm.params.iloc[1] - 1)/np.sqrt(lm.cov_params().iloc[1,1])
            # Compute phi1
            scr2 = np.sum(np.square(residuals(lm)))
            scrc = np.sum(np.square(data.diff().dropna().values))
            phi1 = self._compute_phi(x=scrc,y=scr2,ddl1=2,ddl2=lm.nobs-2)
            teststat = pd.DataFrame({"tau2" : tau2,"phi1" : phi1},index=["statistic"])
        elif typ == "trend":
            data["trend"] = np.arange(1,len(y)+1)
            lm = smf.ols(formula="y~lag(y,1)+trend",data=data).fit()
            tau3 = (lm.params.iloc[1] - 1)/np.sqrt(lm.cov_params().iloc[1,1])
            scr3= np.sum(np.square(residuals(lm)))
            scrc = np.sum(np.square(data.diff().dropna().values))
            # Compute phi2
            phi2 = self._compute_phi(x=scrc,y=scr3,ddl1=3,ddl2=lm.nobs-3)
            # Compute phi3 using anova test
            phi3_reg = smf.ols(formula="diff(y)~1",data=data).fit()
            phi3 = sm.stats.anova_lm(phi3_reg,lm,test="F",typ="I").iloc[1,4]
            teststat = pd.DataFrame({"tau3" : tau3, "phi2" : phi2, "phi3" : phi3},index=["statictic"])

        ##################################################################################
        #       Critical Values
        ##################################################################################
        n = lm.nobs

        if (n < 25):
            rowselec = 0
        elif ((25 <= n) and (n < 50)):
            rowselec = 1
        elif((50 <= n) and (n < 100)):
            rowselec = 2
        elif ((100 <= n) and (n < 250)):
            rowselec = 3
        elif ((250 <= n) and (n < 500)):
            rowselec = 4
        elif (n >= 500):
            rowselec = 5
        
        if typ == "none":
            cval_tau1 = np.array([[-2.66, -1.95, -1.60],
                                  [-2.62, -1.95, -1.61],
                                  [-2.60, -1.95, -1.61],
                                  [-2.58, -1.95, -1.62],
                                  [-2.58, -1.95, -1.62],
                                  [-2.58, -1.95, -1.62]])
            cvals = pd.DataFrame(np.transpose(cval_tau1[rowselec,:]),columns=["tau1"]).T
        elif typ == "drift":
            cval_tau2 = np.array([[-3.75, -3.00, -2.63],
                                  [-3.58, -2.93, -2.60],
                                  [-3.51, -2.89, -2.58],
                                  [-3.46, -2.88, -2.57],
                                  [-3.44, -2.87, -2.57],
                                  [-3.43, -2.86, -2.57]])
            cval_phi1 = np.array([[7.88, 5.18, 4.12],
                                  [7.06, 4.86, 3.94],
                                  [6.70, 4.71, 3.86],
                                  [6.52, 4.63, 3.81],
                                  [6.47, 4.61, 3.79],
                                  [6.43, 4.59, 3.78]])
            cvals = pd.DataFrame(np.c_[cval_tau2[rowselec,:],cval_phi1[rowselec,:]],
                                 columns=["tau2","phi1"]).T
        elif typ == "trend":
            cval_tau3 = np.array([[-4.38, -3.60, -3.24],
                                  [-4.15, -3.50, -3.18],
                                  [-4.04, -3.45, -3.15],
                                  [-3.99, -3.43, -3.13],
                                  [-3.98, -3.42, -3.13],
                                  [-3.96, -3.41, -3.12]])
            
            cval_phi2 = np.array([[8.21, 5.68, 4.67],
                                  [7.02, 5.13, 4.31],
                                  [6.50, 4.88, 4.16],
                                  [6.22, 4.75, 4.07],
                                  [6.15, 4.71, 4.05],
                                  [6.09, 4.68, 4.03]])
            
            cval_phi3 = np.array([[10.61, 7.24, 5.91],
                                  [9.31, 6.73, 5.61],
                                  [8.73, 6.49, 5.47],
                                  [8.43, 6.49, 5.47],
                                  [8.34, 6.30, 5.36],
                                  [8.27, 6.25, 5.34]])  
            cvals = pd.DataFrame(np.c_[cval_tau3[rowselec,:],cval_phi2[rowselec,:],cval_phi3[rowselec,:]],
                                 columns=["tau3","phi2","phi3"]).T
        cvals.columns = ["1pct","5pct","10pct"]

        self.cvals_ = cvals
        self.testreg_ = lm
        self.teststat_ = teststat
        self.model_ = "df"
    
    @staticmethod
    def _compute_phi(x,y,ddl1,ddl2):
        return ((x-y)/ddl1)/(y/ddl2)
    
# Summary df
def summaryDF(self):
    """Summary of Dickey - Fuller unit root test 

    Parameters
    ----------
    self : An instance of class DF

    Returns
    -------
    None
    """

    if self.model_ != "df":
        raise ValueError("Error : 'self' must be and instance of class DF.")
    
    print("####"*20)
    print("#                       Dickey - Fuller Test Unit Root Test                    #")
    print("####"*20)
    print("\n")
    print(self.testreg_.summary().as_text())
    print("\n")
    print("Values of test-statistic :")
    print(self.teststat_)
    print("\n")
    print("Critical values for test statistics :")
    print(self.cvals_)


##########################################################################################################
#           Augmented Dickey - Fuler (ADF) test
###########################################################################################################

class ADF(BaseEstimator,TransformerMixin):
    """Augmented Dickey-Fuller unit root test

    Parameters:
    ----------
    y : {ndarray, Series}
        The data to test for a unit root
    typ : {'none','drift','trend'}, default = 'none'
        The trend component to include in the test

        - "none" - No trend components (Default)
        - "drift" - Include a constant
        - "trend" - Include a constant and linear time trend
    lags : int, optional
        The number of lags to use in the ADF regression.
    selectlags : {"Fixed","AIC","AICC","BIC"}, optional
        The method to use when selecting the lag length

        - "AIC" - Select the minimum of the Akaike IC
        - "AICC" - Select the minimum of the Corrected Akaike IC
        - "BIC" - Select the minimum of the Schwarz/Bayesian IC
    
    Returns
    -------

    Notes
    -----
    The null hypothesis of the Augmented Dickey-Fuller is that there is a unit
    root, with the alternative that there is no unit root. If the pvalue is
    above a critical size, then the null cannot be rejected that there
    and the series appears to be a unit root.

    The p-values are obtained through regression surface approximation from
    MacKinnon (1994) using the updated 2010 tables.
    If the p-value is close to significant, then the critical values should be
    used to judge whether to reject the null.
    """
    def __init__(self,y,typ="none",lags=1,selectlags="Fixed"):

        y = np.array(y)
        data = pd.DataFrame(y,columns=["y"])

        if lags < 0:
            raise ValueError("Error : Lags must be set to an non negative integer value")
        
        if lags > 1:
            if selectlags != "Fixed":
                criterion = pd.DataFrame(np.zeros((lags-1,4)),columns=["lags","AIC","AICC","BIC"]).astype("float")
                for i in np.arange(2,lags+1):
                    if typ == "none":
                        formula = "diff(y)~lag(y,1)+{}-1".format("+".join([f"lag(diff(y),{x})" for x in range(1,i+1)]))
                    elif typ == "drift":
                        formula = "diff(y)~lag(y,1)+{}".format("+".join([f"lag(diff(y),{x})" for x in range(1,i+1)]))
                    elif typ == "trend":
                        data["trend"] = np.arange(1,len(y)+1)
                        formula = "diff(y)~lag(y,1)+{}+trend".format("+".join([f"lag(diff(y),{x})" for x in range(1,i+1)]))
                    lm = smf.ols(formula=formula,data=data).fit()
                    criterion.iloc[i-2,:] = [i,extractAIC(lm),extractAICC(lm),extractBIC(lm)]
                lags = int(criterion.sort_values(by=selectlags).iloc[0,0])
            if typ == "none":
                formula = "diff(y)~lag(y,1)+{}-1".format("+".join([f"lag(diff(y),{x})" for x in range(1,lags+1)]))
                lm = smf.ols(formula=formula,data=data).fit()
                tau1 = lm.params[0]/np.sqrt(lm.cov_params().iloc[0,0])
                teststat = pd.DataFrame({"tau1" : tau1},index=["statistic"])
            elif typ == "drift":
                formula = "diff(y)~lag(y,1)+{}".format("+".join([f"lag(diff(y),{x})" for x in range(1,lags+1)]))
                lm = smf.ols(formula=formula,data=data).fit()
                tau2 = lm.params.iloc[1]/np.sqrt(lm.cov_params().iloc[1,1])
                phi4_formula = "diff(y)~{}-1".format("+".join([f"lag(diff(y),{x})" for x in range(1,lags+1)]))
                phi4_reg = smf.ols(formula=phi4_formula,data=data).fit()
                phi4 = sm.stats.anova_lm(phi4_reg,lm,test="F",typ="I").iloc[1,4]
                teststat = pd.DataFrame({"tau2" : tau2,"phi4" : phi4},index=["statistic"])
            elif typ == "trend":
                data["trend"] = np.arange(1,len(y)+1)
                formula = "diff(y)~lag(y,1)+{}+trend".format("+".join([f"lag(diff(y),{x})" for x in range(1,lags+1)]))
                lm = smf.ols(formula=formula,data=data).fit()
                tau3 = lm.params.iloc[1]/np.sqrt(lm.cov_params().iloc[1,1])
                # Compute phi5
                phi5_formula = "diff(y)~{}-1".format("+".join([f"lag(diff(y),{x})" for x in range(1,lags+1)]))
                phi5_reg = smf.ols(formula=phi5_formula,data=data).fit()
                phi5 = sm.stats.anova_lm(phi5_reg,lm,test="F",typ="I").iloc[1,4]
                # Compute phi6
                phi6_formula = "diff(y)~{}".format("+".join([f"lag(diff(y),{x})" for x in range(1,lags+1)]))
                phi6_reg = smf.ols(formula=phi6_formula,data=data).fit()
                phi6 = sm.stats.anova_lm(phi6_reg,lm,test="F",typ="I").iloc[1,4]
                teststat = pd.DataFrame({"tau3" : tau3, "phi5" : phi5, "phi6" : phi6},index=["statictic"])
        else:
            if typ == "none":
                lm = smf.ols(formula="diff(y)~lag(y,1)+lag(diff(y),1)-1",data=data).fit()
                tau1 = lm.params[0]/np.sqrt(lm.cov_params().iloc[0,0])
                teststat = pd.DataFrame({"tau1" : tau1},index=["statistic"])
            elif typ == "drift":
                lm = smf.ols(formula="diff(y)~lag(y,1)+lag(diff(y),1)",data=data).fit()
                tau2 = lm.params.iloc[1]/np.sqrt(lm.cov_params().iloc[1,1])
                # Compute phi4
                phi4_reg = smf.ols(formula="diff(y)~lag(diff(y),1)-1",data=data).fit()
                phi4 = sm.stats.anova_lm(phi4_reg,lm,test="F",typ="I").iloc[1,4]
                teststat = pd.DataFrame({"tau2" : tau2,"phi4" : phi4},index=["statistic"])
            elif typ == "trend":
                data["trend"] = np.arange(1,len(y)+1)
                lm = smf.ols(formula="diff(y)~lag(y,1)+lag(diff(y),1)+trend",data=data).fit()
                tau3 = lm.params.iloc[1]/np.sqrt(lm.cov_params().iloc[1,1])
                # Compute phi5
                phi5_reg = smf.ols(formula="diff(y)~lag(diff(y),1)-1",data=data).fit()
                phi5 = sm.stats.anova_lm(phi5_reg,lm,test="F",typ="I").iloc[1,4]
                # Compute phi6
                phi6_reg = smf.ols(formula="diff(y)~lag(diff(y),1)",data=data).fit()
                phi6 = sm.stats.anova_lm(phi6_reg,lm,test="F",typ="I").iloc[1,4]
                teststat = pd.DataFrame({"tau3" : tau3, "phi5" : phi5, "phi6" : phi6},index=["statictic"])
        
        ##################################################################################
        #       Critical Values
        ##################################################################################
        n = lm.nobs

        if (n < 25):
            rowselec = 0
        elif ((25 <= n) and (n < 50)):
            rowselec = 1
        elif((50 <= n) and (n < 100)):
            rowselec = 2
        elif ((100 <= n) and (n < 250)):
            rowselec = 3
        elif ((250 <= n) and (n < 500)):
            rowselec = 4
        elif (n >= 500):
            rowselec = 5
        
        if typ == "none":
            cval_tau1 = np.array([[-2.66, -1.95, -1.60],
                                  [-2.62, -1.95, -1.61],
                                  [-2.60, -1.95, -1.61],
                                  [-2.58, -1.95, -1.62],
                                  [-2.58, -1.95, -1.62],
                                  [-2.58, -1.95, -1.62]])
            cvals = pd.DataFrame(np.transpose(cval_tau1[rowselec,:]),columns=["tau1"]).T
        elif typ == "drift":
            cval_tau2 = np.array([[-3.75, -3.00, -2.63],
                                  [-3.58, -2.93, -2.60],
                                  [-3.51, -2.89, -2.58],
                                  [-3.46, -2.88, -2.57],
                                  [-3.44, -2.87, -2.57],
                                  [-3.43, -2.86, -2.57]])
            cval_phi1 = np.array([[7.88, 5.18, 4.12],
                                  [7.06, 4.86, 3.94],
                                  [6.70, 4.71, 3.86],
                                  [6.52, 4.63, 3.81],
                                  [6.47, 4.61, 3.79],
                                  [6.43, 4.59, 3.78]])
            cvals = pd.DataFrame(np.c_[cval_tau2[rowselec,:],cval_phi1[rowselec,:]],
                                 columns=["tau2","phi4"]).T
        elif typ == "trend":
            cval_tau3 = np.array([[-4.38, -3.60, -3.24],
                                  [-4.15, -3.50, -3.18],
                                  [-4.04, -3.45, -3.15],
                                  [-3.99, -3.43, -3.13],
                                  [-3.98, -3.42, -3.13],
                                  [-3.96, -3.41, -3.12]])
            
            cval_phi2 = np.array([[8.21, 5.68, 4.67],
                                  [7.02, 5.13, 4.31],
                                  [6.50, 4.88, 4.16],
                                  [6.22, 4.75, 4.07],
                                  [6.15, 4.71, 4.05],
                                  [6.09, 4.68, 4.03]])
            
            cval_phi3 = np.array([[10.61, 7.24, 5.91],
                                  [9.31, 6.73, 5.61],
                                  [8.73, 6.49, 5.47],
                                  [8.43, 6.49, 5.47],
                                  [8.34, 6.30, 5.36],
                                  [8.27, 6.25, 5.34]])  
            cvals = pd.DataFrame(np.c_[cval_tau3[rowselec,:],cval_phi2[rowselec,:],cval_phi3[rowselec,:]],
                                 columns=["tau3","phi5","phi6"]).T
        cvals.columns = ["1pct","5pct","10pct"]

        self.cvals_ = cvals
        self.testreg_ = lm
        self.teststat_ = teststat
        self.model_ = "adf"

# Summary ADF
def summaryADF(self):
    """Summary of Augmented Dickey Fuller unit root test

    Parameters
    ----------
    self : An instance of class ADF.

    Returns
    -------
    None
    """

    if self.model_ != "adf":
        raise ValueError("Error : 'self' must be and instance of class ADF.")
    
    print("####"*20)
    print("#                   Augmented Dickey - Fuller Unit Root Test                   #")
    print("####"*20)
    print("\n")
    print(self.testreg_.summary().as_text())
    print("\n")
    print("Values of test-statistic :")
    print(self.teststat_)
    print("\n")
    print("Critical values for test statistics :")
    print(self.cvals_)


#######################################################################################################
#     Phiulips Perron Test (PP)
#########################################################################################################


class PP(BaseEstimator,TransformerMixin):
    """Phillips-Perron unit root test

    Parameters:
    ----------
    x : {ndarray, Series}
        The data to test for a unit root
    typ : {'Z-tau','Z-alpha'}, default = 'Z-alpha'
    model : {'constant','trend'}, default = 'constant'
    lags : {'short','long'}, default = 'short'
    use_lag : int or None, optional

    Returns
    -------

    """

    def __init__(self,x,typ="Z-alpha",model="constant",lags="short",use_lag=None):

        x = np.array(x)
        y = x[1:]
        data = pd.DataFrame(y,columns=["y"])
        data["y_l1"] =  x[:-1]
        n = len(x) - 1

        if use_lag is not None:
            lmax = int(use_lag)
            if lmax < 0:
                print(warnings.warn("use_lag has to be positive and integer; lags='short' used."))
                lmax = math.trunc(4*(n/100)**(0.25))
        elif lags == "short":
            lmax = math.trunc(4*(n/100)**(0.25))
        elif lags == "long":
            lmax = math.trunc(12*(n/100)**(0.25))
        
        if model == "trend":
            cvals = pd.DataFrame({"1pct":-3.9638-8.353/n-47.44/(n**2),
                                  "5pct":-3.4126-4.039/n-17.83/(n**2),
                                  "10pct":-3.1279-2.418/n-7.58/(n**2)},
                                  index=["critical values"])
            data["trend"] = np.arange(1,n+1) - n/2
            modelname = "with intercept and trend"
            lm = smf.ols(formula="y~y_l1+trend",data=data).fit()
            res = residuals(lm)
            mytstat = lm.tvalues[0]
            betatstat = lm.tvalues[2]
            s = np.mean(np.square(res))
            myybar = (1/n)*np.var(y)
            myy = (1/n)*np.mean(np.square(y))
            mty = (n**(-5/2))*np.arange(1,n+1).dot(y)
            my = (n**(-3/2))*np.sum(y)
            idx = np.arange(1,lmax+1)
            coprods = np.array(list(map(lambda l : np.dot(res[l:],res[:-l]),idx)))
            weights = 1 - idx/(lmax+1)
            sig = s + (2/n)*np.dot(weights,coprods)
            lambd = 0.5*(sig - s)
            lambdprime = lambd/sig
            M = (1-n**(-2))*myy - 12*mty**2 + 12*(1 + 1/n)*mty*my - (4 + 6/n + 2/n**2)*my**2
            mystat = math.sqrt(s/sig)*mytstat - lambdprime*math.sqrt(sig)*my/(math.sqrt(M)*math.sqrt((M+my**2)))
            betastat = math.sqrt(s/sig)*betatstat - lambdprime*math.sqrt(sig)*(0.5*my - mty)/(math.sqrt(M/12)*math.sqrt(myybar))
            auxstat = pd.DataFrame({"Z-tau-mu" : mystat,"Z-tau-beta":betastat},index=["aux. Z statistics"]).T
            if typ == "Z-tau":
                tstat = (lm.params[1]-1)/math.sqrt(lm.cov_params().iloc[1,1])
                teststat = math.sqrt(s/sig)*tstat-lambdprime*math.sqrt(sig)/math.sqrt(M)
            elif typ == "Z-alpha":
                alpha = lm.params[1]
                teststat = n*(alpha-1)-lambd/M
                cvals = pd.DataFrame({"1pct":np.nan,"5pct":np.nan,"10pct":np.nan},index=["critical values"])
        elif model == "constant":
            cvals = pd.DataFrame({"1pct":-3.4335-5.999/n-29.25/(n**2),
                                 "5pct":-2.8621-2.738/n-8.36/(n**2),
                                 "10pct":-2.5671-1.438/n-4.48/(n**2)},
                                 index=["critical values"])
            lm = smf.ols(formula="y~y_l1",data=data).fit()
            modelname = "with intercept"
            res = residuals(lm)
            mytstat = lm.tvalues[0]
            s = np.mean(np.square(res))
            myybar = (1/n)*np.var(y)
            myy = (1/n)*np.mean(np.square(y))
            mty = (n**(-5/2))*np.arange(1,n+1).dot(y)
            my = (n**(-3/2))*np.sum(y)
            idx = np.arange(1,lmax+1)
            coprods = np.array(list(map(lambda l : np.dot(res[l:],res[:-l]),idx)))
            weights = 1 - idx/(lmax+1)
            sig = s + (2/n)*np.dot(weights,coprods)
            lambd = 0.5*(sig - s)
            lambdprime = lambd/sig
            mystat = math.sqrt(s/sig)*mytstat + lambdprime*math.sqrt(sig)*my/(math.sqrt(myy)*math.sqrt(myybar))
            auxstat = pd.DataFrame({"aux. Z statistics" : mystat},index=["Z-tau-mu"])
            if typ == "Z-tau":
                tstat = (lm.params[1]-1)/math.sqrt(lm.cov_params().iloc[1,1])
                teststat = math.sqrt(s/sig)*tstat-lambdprime*math.sqrt(sig)/math.sqrt(myybar)
            elif typ =="Z-alpha":
                alpha = lm.params[1]
                teststat = n*(alpha-1)-lambd/myybar
                cvals = pd.DataFrame({"1pct":np.nan,"5pct":np.nan,"10pct":np.nan},index=["critical values"])
        
        self.cvals_ = cvals
        self.testreg_ = lm
        self.teststat_ = teststat
        self.auxstat_ = auxstat
        self.modelname_ = modelname
        self.model_ = "pp"


# Summary PP
def summaryPP(self):
    """
    
    
    """

    if self.model_ != "pp":
        raise ValueError("Error : 'self' must be and instance of class PP.")
    
    print("####"*20)
    print("#                        Phillips - Perron Unit Root Test                      #")
    print("####"*20)
    print("Model " + self.modelname_)
    print("\n")
    print(self.testreg_.summary().as_text())
    print("\n")
    print(f"Values of test-statistic : {self.teststat_}\n")
    print("Critical values for test statistics :")
    print(self.cvals_)
    print("\n")
    print(self.auxstat_)



##############################################################################################
#                   Kwiatkowski, Phillips, Schmidt and Shin (KPSS) stationarity test
###########################################################################################

class KPSS(BaseEstimator,TransformerMixin):
    """Kwiatkowski, Phillips, Schmidt and Shin (KPSS) stationarity test

    Parameters:
    ----------
    x : {ndarray, Series}
        The data to test for a unit root
    typ : {'mu','tau'}, default = 'tau '
    model : {'constant','trend'}, default = 'constant'
    lags : {'short','long',"nil"}, default = 'short'
    use_lag : int or None, optional

    Returns
    -------      
    """
    def __init__(self,y,typ = "mu",lags="short",use_lag = None):

        y = np.array(y)
        data = pd.DataFrame(y,columns=["y"])
        n = len(y)

        if use_lag is not None:
            lmax = int(use_lag)
            if lmax < 0:
                print(warnings.warn("use_lag has to be positive and integer; lags='short' used."))
                lmax = math.trunc(4*(n/100)**(0.25))
        elif lags == "short":
            lmax = math.trunc(4*(n/100)**(0.25))
        elif lags == "long":
            lmax = math.trunc(12*(n/100)**(0.25))
        elif lags == "nil":
            lmax = 0
        
        if typ == "mu":
            cvals = pd.DataFrame({"10pct" : 0.347, "5pct" : 0.463, "2.5pct":0.574,"1pct":0.739},index=["critical values"])
            res = y - np.mean(y)
        elif typ == "tau":
            cvals = pd.DataFrame({"10pct": 0.119, "5pct" : 0.146,"2.5pct":0.176,"1pct":0.216},index=["critical values"])
            data["trend"] = np.arange(1,n+1)
            res = smf.ols(formula="y~trend",data=data).fit().resid
        
        S = np.cumsum(res)
        nume = np.mean(np.square(S))/n
        s2 = np.mean(np.square(res))
        if lmax == 0:
            denom = s2
        else:
            idx = np.arange(1,lmax+1)
            xcov = np.array(list(map(lambda l : np.dot(res[l:],res[:-l]),idx)))
            bartlett = 1 - idx/(lmax+1)
            denom = s2 + (2/n)*np.dot(bartlett,xcov)
        
        teststat = nume/denom

        self.teststat_ = teststat
        self.cvals_ = cvals
        self.model_ = "kpss"



# Summary KPSS
def summaryKPSS(self):
    """
    
    
    """

    if self.model_ != "kpss":
        raise ValueError("Error : 'self' must be and instance of class KPSS.")
    
    print("####"*17)
    print("#       Kwiatkowski, Phillips, Schmidt and Shin Unit Root Test     #")
    print("####"*17)
    print("\n")
    print(f"Values of test-statistic : {self.teststat_}\n")
    print("Critical values for test statistics :")
    print(self.cvals_)

###########################################################################################
#     Elliott, Rothenberg and Stock-Test GLS detrended Dickey-Fuller
###########################################################################################


class ERS(BaseEstimator,TransformerMixin):
    """

    Parameters
    ----------
    
    
    
    """
    def __init__(self,y,typ="DF-GLS",model="constant",lag_max=4):
        raise NotImplementedError("Error : This method is not yet implemented")

        if lag_max < 0:
            print(warnings.warn("lag_max bust be greater or equal to one and integer; setting lag_max=4"))
            lag_max = 4
        
        lag_max = lag_max + 1
        idx= np.arange(2,lag_max+1)
        y = np.array(y)
        data = pd.DataFrame(y,columns=["y"])
        nobs = len(y)

        if nobs < 50:
            rowsel = 0
        elif nobs < 100:
            rowsel = 1
        elif nobs <= 200:
            rowsel = 2
        elif nobs > 200:
            rowsel = 3
        
        if model == "constant":
            ahat = 1 - 7.0/nobs
            data["ya"] = np.r_[y[0],y[1:] - ahat*y[:-1]]
            data["za1"] = np.r_[1,np.repeat(1-ahat,nobs-1)]
            lm = smf.ols(formula="ya~za1-1",data=data).fit()
            yd = y - lm.params[0]
        elif model == "trend":
            ahat = 1 - 13.5/nobs
            data["ya"] = np.r_[y[0],y[1:] - ahat*y[:-1]]
            data["za1"] = np.r_[1,np.repeat(1-ahat,nobs-1)]
            trend = np.arange(1,nobs+1)
            data["za2"] = np.r_[1,trend[1:] - ahat*trend[:-1]]
            lm = smf.ols(formula="ya~za1+za2-1",data=data).fit()
            yd = y - lm.params[0] - lm.params[1]*trend
        
        def what(x,z=y):
            pass

        if typ == "P-test":
            cvals_ptest =  {"constant" : np.array([[1.87,2.97,3.91],[1.95,3.11,4.17],[1.91,3.17,4.33],[1.99,3.26,4.48]]),
                            "trend" : np.array([[4.22,5.72,6.77],[4.26,5.64,6.79],[4.05,5.66,6.86],[3.96,5.62,6.89]])}
            res = residuals(lm)
            if model == "constant":
                null_res = np.r_[0,diff(y)]
                cvals = pd.DataFrame(cvals_ptest[model][rowsel,:],index=["1pct", "5pct", "10pct"]).T
                model_name = "with intercept"
            elif model == "trend":
                null_res = np.r_[0,diff(y)]
                null_res = null_res - np.mean(y)
                cvals = pd.DataFrame(cvals_ptest[model][rowsel,:],index=["1pct", "5pct", "10pct"]).T
                model_name = "with intercept and trend"
            
            sig_null = np.sum(null_res**2)
            sig_res = np.sum(res**2)
            if lag_max > 1:
                pass
            elif lag_max <= 1:
                what_reg = smf.ols(formula="diff(y)~lag(y,1)",data=data).fit()
                sumlc = 0
                lag_max = lag_max - 1

            what_sq = 1.0
            teststat = (sig_res - ahat*sig_null)/what_sq
            test_reg = None
        elif typ == "DF-GLS":
            if model == "constant":
                cvals = pd.DataFrame(np.r_[-2.5658-1.960/nobs-10.04/(nobs**2),-1.9393-0.398/nobs,-1.6156-0.181/nobs],index=["1pct", "5pct", "10pct"]).T
                cvals.index = ["critical values"]
            elif model == "trend":
                cvals_dfgls_tau = -1*np.array([[3.77,3.19,2.89],[3.58,3.03,2.74],[3.46,2.93,2.64],[3.48,2.89,2.57]])
                cvals =  pd.DataFrame(cvals_dfgls_tau[rowsel,:],index=["1pct", "5pct", "10pct"]).T


        self.model_ = "ers"










