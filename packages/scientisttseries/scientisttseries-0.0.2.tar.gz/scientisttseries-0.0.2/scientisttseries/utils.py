#

import numpy as np
import pandas as pd
from statsmodels.tools import eval_measures
from statsmodels.stats.outliers_influence import OLSInfluence, GLMInfluence
import statsmodels as smt
from sklearn import metrics

# Lag function
def lag(x,n):
    if n==0:
        return x
    elif isinstance(x,pd.Series):
        return x.shift(n)
    elif isinstance(x,np.array):
        x = pd.Series(x)
        return x.shift(n)
    else:
        x = x.copy()
        x[n:] = x[0:-n]
        x[:n] = np.nan
        return x

# Diff Function
def diff(x):
    if isinstance(x,pd.Series):
        return x.diff()
    else:
        x = pd.Series(x)
        return x.diff()

# Extract AIC
def extractAIC(self):
    """
    Parameters
    ----------
    self : an instance of statsmodels

    Returns
    -------
    aic : float
    """
    # Number of observations
    nobs = self.nobs
    # Log - likelihood
    llf = self.llf
    # Number of parameters
    k = len(self.params)
    return eval_measures.aic(llf=llf,nobs=nobs,df_modelwc=k)

def extractBIC(self):
    # Number of observations
    nobs = self.nobs
    # Log - likelihood
    llf = self.llf
    # Number of parameters
    k = len(self.params)
    return eval_measures.bic(llf=llf,nobs=nobs,df_modelwc=k)

def extractAICC(self):
    # Number of observations
    nobs = self.nobs
    # Log - likelihood
    llf = self.llf
    # Number of parameters
    k = len(self.params)
    return eval_measures.aicc(llf=llf,nobs=nobs,df_modelwc=k)

# Extract residuals
def residuals(self, choice="response"):
    """
    Extract Model Residuals

    Parameters
    ----------
    self : an object for which the extraction of model residuals is meaningful.
    choice : {"response","pearson","deviance"}, default = "absolu". 
                - "response" : The response residuals
                - "pearson" : Pearson residuals
                - "deviance" : Deviance residuals. (Only used for logistic regression model.)

    Returns
    -------
    Series : pd.Series
    """
    if self.model.__class__ == smt.regression.linear_model.OLS:
        if choice == "response":
            return self.resid # The residuals of the model.
        elif choice == "pearson":
            return self.resid_pearson # Residuals, normalized to have unit variance.
    elif self.model.__class__ == smt.discrete.discrete_model.Logit:
        if choice == "response": # The residuals of the model.
            return self.resid_response
        elif choice == "pearson":
            return self.resid_pearson # Residuals, normalized to have unit variance.
        elif choice == "deviance":
            return self.resid_dev
    elif self.model.__class__ == smt.tsa.arima.model.ARIMA:
        return self.resid
    

def rstandard(self,choice="rpearson"):
    """
    Extract Standardized Model residuals

    Parameters
    ----------
    self : an object for which the extraction of model residuals is meaningful.
    choice : {"rpearson","rdeviance"}, default = "rpearson".
             Only used for logistic regression model.
                - "rpearson" : Standardized Pearson residuals
                - "rdeviance" : Standardized deviance residuals

    Returns
    -------
    Series : 
    """
    # Extract resid
    if self.model.__class__ == smt.regression.linear_model.OLS:
        influ = OLSInfluence(self)
        sigma = np.sqrt(self.scale)
    elif self.model.__class__ == smt.discrete.discrete_model.Logit:
        influ = GLMInfluence(self)
        hii = influ.hat_matrix_diag
        if choice == "rpearson":
            return residuals(self,choice="pearson")/np.sqrt(1 - hii)
        elif choice == "rdeviance":
            return residuals(self,choice="deviance")/np.sqrt(1 - hii)
        
def rstudent(self):
    """
    Studentized residuals

    Parameters
    ----------
    self : an object of class OLS,

    Returns
    -------
    Series
    """
    if self.model.__class__ == smt.regression.linear_model.OLS:
        influ = OLSInfluence(self)
        return influ.resid_studentized_external
    elif self.model.__class__ == smt.discrete.discrete_model.Logit:
        influ = GLMInfluence(self)
        return influ.resid_studentized

def coefficients(self):
    """
    
    """
    return self.summary().tables[1]

def compare_performance(model=list()):
    """
    Parameters
    ----------
    model : list of training model to compare

    Returns
    -------
    DataFrame
    """

    def evaluate(i,name):
        res = pd.DataFrame({"AIC" : extractAIC(name), # Akaike information criterion.
                            "AICC":extractAICC(name), # 
                             "BIC" : extractBIC(name), # Bayesian information criterion.
                             "Log-Likelihood" : name.llf}, # Log-likelihood of model
                             index=["Model " + str(i+1)])
        if name.model.__class__  == smt.regression.linear_model.OLS:
            res["R-squared"] = name.rsquared
            res["Adj. rsquared"] = name.rsquared_adj
            ytrue, ypred= name.model.endog, name.predict()
            res["RMSE"] = metrics.mean_squared_error(y_true=ytrue,y_pred=ypred,squared=True)
            res["sigma"] = np.sqrt(name.scale)
            res.insert(0,"Name","ols")
        elif name.model.__class__ == smt.discrete.discrete_model.Logit:
            res["Pseudo R-squared"] = name.prsquared  # McFadden's pseudo-R-squared.
            ytrue, yprob = name.model.endog, name.predict()
            ypred = np.where(yprob > 0.5, 1, 0)
            res["log loss"] = metrics.log_loss(y_true=ytrue,y_pred=ypred)
            res.insert(0,"Name","logit")
        elif name.model.__class__ == smt.tsa.arima.model.ARIMA:
            res["MAE"] = name.mae
            res["RMSE"] = np.sqrt(name.mse)
            res["SSE"] = name.sse
            res.insert(0,"Name","arima")
        return res
    res1 = pd.concat(map(lambda x : evaluate(x[0],x[1]),enumerate(model)),axis=0)
    return res1
        
    



