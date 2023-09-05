############################################################################################################
#
#   https://github.com/robjhyndman/forecast/tree/master
#
############################################################################################################

import pandas as pd
import plotnine as pn
import numpy as np
import scipy.stats as st
from statsmodels.tsa.stattools import acf, pacf

def ic_alpha(alpha,n):
    return st.norm.ppf((1 + (1 - alpha))/2)/np.sqrt(n)

def ggtsplot(data=pd.Series,
             xlabel=None,
             ylabel=None,
             title=None,
             alpha = 1,
             color="black",
             linetype="solid",
             size=0.5,
             ggtheme = pn.theme_gray()):
    """
    Plotting Time Series Objects. Description. Visualization functions for time series object.

    Parameters:
    -----------
    data : Pandas series.
           Series of time-series values.
    xlabel : str, optional.
          labels the x-axis of the current axes or standalone visualization.   Default is 'None'.
    ylabel : str, optional.
        labels the y-axis of the current axes or standalone visualization. Default is 'None'.
    title : str, optional
        Title to place on plot.  Default is 'None'.
    alpha : float, default = 1.
    color : str, default = "black".
    linetype : str, default = "solid".
    size : float, default = 0.5

    Return:
    -------
    Figure
    """
    if not isinstance(data,pd.Series):
        raise ValueError("Error : 'data' must be a series. See 'https://pandas.pydata.org/docs/reference/api/pandas.Series.html'.")

    # Extract name
    data = data.to_frame()
    name = data.columns[0]

    # Initialise
    p = (pn.ggplot(data,pn.aes(x=data.index,y=name))+
            pn.geom_line(alpha=alpha,color=color,linetype=linetype,size=size))

    if title is None:
        title = name
    if xlabel is None:
        xlabel = "Time"
    if ylabel is None:
        ylabel = "value"
    
    p =p + pn.labs(x=xlabel,y=ylabel,title=title)

    # Add Theme
    p = p + ggtheme
    return p

############################################################################################################
#           Autocorrelation Function (ACF)
############################################################################################################

def ggacf(x, 
          xlabel = None,
          ylabel = None,
          title=None,
          auto_ylims = False,
          adjusted=False,
          lags=None, 
          fft=True,
          alpha=0.05,
          bartlett_confint=True,
          missing='none',
          zero = True,
          ggtheme = pn.theme_gray()):
    
    """
    Plot the autocorrelation function

    Plots lags on the horizontal and the correlations on vertical axis.

    Parameters
    ----------
    x : array_like
        Array of time-series values
    xlabel : str, optional
        labels the x-axis of the current axes or standalone visualization.   Default is 'None'
    ylabel : str, optional
        labels the y-axis of the current axes or standalone visualization. Default is 'None'
    title : str, optional
        Title to place on plot.  Default is 'None'
    auto_ylims : bool, optional
        If True, adjusts automatically the y-axis limits to ACF values.
    adjusted : bool
        If True, then denominators for autocovariance are n-k, otherwise n
    lags : {int, array_like}, optional
        An int or array of lag values, used on horizontal axis. Uses
        np.arange(lags) when lags is an int.  If not provided,
        ``lags=np.arange(len(corr))`` is used.
    fft : bool, optional
        If True, computes the ACF via FFT.
    alpha : scalar, optional
        If a number is given, the confidence intervals for the given level are
        returned. For instance if alpha=.05, 95 % confidence intervals are
        returned where the standard deviation is computed according to
        Bartlett's formula. If None, no confidence intervals are plotted.
    bartlett_confint : bool, default True
        Confidence intervals for ACF values are generally placed at 2
        standard errors around r_k. The formula used for standard error
        depends upon the situation. If the autocorrelations are being used
        to test for randomness of residuals as part of the ARIMA routine,
        the standard errors are determined assuming the residuals are white
        noise. The approximate formula for any lag is that standard error
        of each r_k = 1/sqrt(N). See section 9.4 of [1] for more details on
        the 1/sqrt(N) result. For more elementary discussion, see section
        5.3.2 in [2].
        For the ACF of raw data, the standard error at a lag k is
        found as if the right model was an MA(k-1). This allows the
        possible interpretation that if all autocorrelations past a
        certain lag are within the limits, the model might be an MA of
        order defined by the last significant autocorrelation. In this
        case, a moving average model is assumed for the data and the
        standard errors for the confidence intervals should be
        generated using Bartlett's formula. For more details on
        Bartlett formula result, see section 7.2 in [1].
    missing : str, optional
        A string in ['none', 'raise', 'conservative', 'drop'] specifying how
        the NaNs are to be treated.
    zero : bool, optional
        Flag indicating whether to include the 0-lag autocorrelation.
        Default is True.
   ggtheme : plotnine themes. Default is 'theme_gray()'

    Returns
    -------
    Figure
    """

    acf_x = acf(x=x,
                nlags=lags,
                alpha=alpha,
                fft=fft,
                bartlett_confint=bartlett_confint,
                adjusted=adjusted,
                missing=missing)
    
    if alpha is not None:
        acf_x, confint = acf_x[:2]
        # IC alpha
        lim1= ic_alpha(alpha, len(x))
        lim0 = -lim1
    
    # Store all informations
    acf_df = pd.DataFrame({"Lag"  : np.arange(len(acf_x)) ,"ACF"  : acf_x})

    # Remove First Row
    if not zero:
        acf_df = acf_df.drop(index=[0])

    
    # Initialize
    p = (pn.ggplot(data=acf_df,mapping=pn.aes(x = "Lag",y="ACF"))+
         pn.geom_hline(mapping=pn.aes(yintercept=0))+
         pn.geom_segment(mapping=pn.aes(xend="Lag",yend=0)))
    
    if alpha is not None:
        p = (p + pn.geom_hline(mapping=pn.aes(yintercept=lim1),linetype="dashed",color="blue")+
             pn.geom_hline(mapping=pn.aes(yintercept=lim0),linetype="dashed",color="blue"))
    
    # y lim
    if auto_ylims is False:
        p = p + pn.ylim((-1,1))
    
    # Set xlabel, ylabel and title values
    if xlabel is None:
        xlabel = "Lag"
    if ylabel is None:
        ylabel = "ACF"
    if title is None:
        title = "Autocorrelation"
    
    p = p +pn.labs(x=xlabel,y=ylabel,title=title)
    
    # Add Theme
    p = p + ggtheme

    return p


###############################################################################################
#       Partial Autocorrelation Function (PACF)
###############################################################################################

def ggpacf(x,
           xlabel = None,
           ylabel = None,
           title = None,
           lags = None,
           alpha = 0.05,
           method="ywm",
           zero=True,
           ggtheme = pn.theme_gray()):
    
    """
    Plot the partial autocorrelation function

    Parameters
    ----------
    x : array_like
        Array of time-series values
    xlabel : str, optional
        labels the x-axis of the current axes or standalone visualization.   Default is 'None'
    ylabel : str, optional
        labels the y-axis of the current axes or standalone visualization. Default is 'None'
    title : str, optional
        Title to place on plot.  Default is 'None'
    lags : {int, array_like}, optional
        An int or array of lag values, used on horizontal axis. Uses
        np.arange(lags) when lags is an int.  If not provided,
        ``lags=np.arange(len(corr))`` is used.
    alpha : float, optional
        If a number is given, the confidence intervals for the given level are
        returned. For instance if alpha=.05, 95 % confidence intervals are
        returned where the standard deviation is computed according to
        1/sqrt(len(x))
    method : str
        Specifies which method for the calculations to use:

        - "ywm" or "ywmle" : Yule-Walker without adjustment. Default.
        - "yw" or "ywadjusted" : Yule-Walker with sample-size adjustment in
          denominator for acovf. Default.
        - "ols" : regression of time series on lags of it and on constant.
        - "ols-inefficient" : regression of time series on lags using a single
          common sample to estimate all pacf coefficients.
        - "ols-adjusted" : regression of time series on lags with a bias
          adjustment.
        - "ld" or "ldadjusted" : Levinson-Durbin recursion with bias
          correction.
        - "ldb" or "ldbiased" : Levinson-Durbin recursion without bias
          correction.
    zero : bool, optional
        Flag indicating whether to include the 0-lag autocorrelation.
        Default is True.
    ggtheme : plotnine themes. Default is 'theme_gray()'

    Returns
    -------
    Figure
    """
    
    pacf_x = pacf(x=x,
                  nlags=lags,
                  method=method,
                  alpha=alpha)
    
    if alpha is not None:
        pacf_x, confint = pacf_x[:2]
        # IC alpha
        lim1= ic_alpha(alpha, len(x))
        lim0 = -lim1
    
    # Store all informations
    pacf_df = pd.DataFrame({"Lag"  : np.arange(len(pacf_x)) ,"PACF"  : pacf_x})

    # Remove First Row
    if not zero:
        pacf_df = pacf_df.drop(index=[0])

    # Initialize
    p = (pn.ggplot(data=pacf_df,mapping=pn.aes(x = "Lag",y="PACF"))+
         pn.geom_hline(mapping=pn.aes(yintercept=0))+
         pn.geom_segment(mapping=pn.aes(xend="Lag",yend=0)))
    
    if alpha is not None:
        p = (p + pn.geom_hline(mapping=pn.aes(yintercept=lim1),linetype="dashed",color="blue")+
             pn.geom_hline(mapping=pn.aes(yintercept=lim0),linetype="dashed",color="blue"))
    
    # Set xlabel, ylabel and title values
    if xlabel is None:
        xlabel = "Lag"
    if ylabel is None:
        ylabel = "Partial ACF"
    if title is None:
        title = "Partial Autocorrelation"
    
    p = p + pn.xlab(xlabel)+pn.ylab(ylabel)+pn.ggtitle(title)
    
    # Add Theme
    p = p + ggtheme

    return p

##################################################################################################
#           Seasonal Plot
##################################################################################################

def ggseasonplot(X,ylabel=None,title=None):
    """
    
    """
    if not isinstance(X,pd.Series):
        raise ValueError("Error : 'data' must be a series. See 'https://pandas.pydata.org/docs/reference/api/pandas.Series.html'.")
    
    # Check seasonal
    freq = pd.infer_freq(X.index)

    if freq == "M":
        season = 12
        xlabel = "Month"
        xtickslabels = ["Jan","Fev","Mar","Apr","May","Jun","Jul","Aou","Sep","Oct","Nov","Dec"]
    if freq == "W":
        season = 7
        xlabel = "Week"
        xtickslabels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    if freq in ["Q","Q-DEC"]:
        season = 4
        xlabel = "Quarter"
        xtickslabels = ["Q"+str(x+1) for x in range(season)]
    
    # Create
    data = pd.DataFrame({"y":X, "year" : X.index.year,"cycle":X.index.month,"time" : (X.index.month - 1)/season})
    data.year =  data.year.astype("category")

    # Initialise ggplot object
    p = pn.ggplot(data,pn.aes(x="time",y="y",group="year",colour="year"))
    
    ## Add 
    p = p + pn.geom_line()

    if ylabel is None:
        ylabel = X.name

    if title is None:
        title = "Seasonal plot"

    breaks = np.sort(np.unique(data.time))
    p = p + pn.scale_x_continuous(breaks = breaks, minor_breaks = None, labels = xtickslabels)
    
    p = p + pn.labs(title=title,x=xlabel,y=ylabel)
    return p

########################################
#       Plot predict
############################################

def ggpredict(res,
              start=None,
              end = None,
              dynamic=False,
              alpha = 0.05,
              ggtheme = pn.theme_gray(),
              **kwargs):
    
    """

    Parameters
    ----------
    result : Result
        Any model result supporting ``get_prediction``.
    start : int, str, or datetime, optional
        Zero-indexed observation number at which to start forecasting,
        i.e., the first forecast is start. Can also be a date string to
        parse or a datetime type. Default is the the zeroth observation.
    end : int, str, or datetime, optional
        Zero-indexed observation number at which to end forecasting, i.e.,
        the last forecast is end. Can also be a date string to
        parse or a datetime type. However, if the dates index does not
        have a fixed frequency, end must be an integer index if you
        want out of sample prediction. Default is the last observation in
        the sample.
    dynamic : bool, int, str, or datetime, optional
        Integer offset relative to `start` at which to begin dynamic
        prediction. Can also be an absolute date string to parse or a
        datetime type (these are not interpreted as offsets).
        Prior to this observation, true endogenous values will be used for
        prediction; starting with this observation and continuing through
        the end of prediction, forecasted endogenous values will be used
        instead.
    alpha : {float, None}
        The tail probability not covered by the confidence interval. Must
        be in (0, 1). Confidence interval is constructed assuming normally
        distributed shocks. If None, figure will not show the confidence
        interval.
     ggtheme : plotnine themes. Default is 'theme_gray()'
    **kwargs
        Any additional keyword arguments to pass to ``result.get_prediction``.

    Returns
    -------
    Figure
    """
    
    pred = res.get_prediction(start=start,end=end,dynamic=dynamic,**kwargs)
    mean = pred.predicted_mean
    if isinstance(mean, (pd.Series, pd.DataFrame)):
        x = mean.index
        #mean.plot(ax=ax, label="forecast")
    else:
        x = np.arange(mean.shape[0])
        #ax.plot(x, mean)
    
    pred_df = pd.DataFrame({"x" : x, "y" : mean})

    p = pn.ggplot(pred_df,pn.aes(x="x",y="y"))+pn.geom_line(color="black")

    if alpha is not None:
        label = f"{1-alpha:.0%} confidence interval"
        ci = pred.conf_int(alpha)
        conf_int = np.asarray(ci)

        p= p + pn.geom_ribbon(pn.aes(ymin=conf_int[:, 0],ymax=conf_int[:, 1]),fill="gray",alpha=0.5)
    
    # Add theme
    p = p + ggtheme
    
    return p


