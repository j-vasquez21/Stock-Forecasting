# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import itertools
# from sklearn.metrics import mean_squared_error
# from sklearn.linear_model import LinearRegression
# from sklearn.model_selection import TimeSeriesSplit
# import seaborn as sns
# sns.set_palette("vlag")

# #from statsmodels.tsa.arima.model import ARIMA
# from statsmodels.tsa.stattools import acf, pacf, adfuller
# from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
# from statsmodels.tsa.statespace.sarimax import SARIMAX
# from statsmodels.tsa.seasonal import seasonal_decompose

# import warnings
# warnings.simplefilter('ignore')

# Check Stationarity
def check_stationarity(ts):
    #Determing rolling statistics
    roll_mean = ts.rolling(30).mean()
    roll_std = ts.rolling(30).std()
    #Plot rolling statistics:
    plt.plot(ts, color='blue',label='Original')
    plt.plot(roll_mean, color='red', label='Rolling Mean')
    plt.plot(roll_std, color='black', label = 'Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean and Standard Deviation')
    plt.show(block=False)

    print("Results of dickey fuller test")
    adft = adfuller(ts,autolag='AIC')
    # output for dft will give us without defining what the values are.
    #hence we manually write what values does it explains using a for loop
    output = pd.Series(adft[0:4],index=['Test Statistics','p-value','No. of lags used','Number of observations used'])
    for key,values in adft[4].items():
        output['critical value (%s)'%key] =  values
    print(output)
    return ""

# Apply Differencing to a Time Series
def differenced(tick,k,test=False):
    ts = funds.loc[tick,['close']]
    ts_diff = ts.diff(k).dropna()
    if test == True:
        print(f"Differencing Results For {tick}:")
        print(check_stationarity(ts_diff));
    else:
        return ts_diff
    return ""
# Apply Decomposition to a Time Series
def decompose(z,target,plot=False,check=False):
    ts = funds.loc[z,[target]]
    decomposition = seasonal_decompose(ts,period=30)
    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid
    if plot == True:
        plt.figure(figsize=(18,10))
        plt.subplot(411)
        plt.plot(ts, label='Original', color='blue')
        plt.legend(loc='best')
        plt.subplot(412)
        plt.plot(trend, label='Trend', color='blue')
        plt.legend(loc='best')
        plt.subplot(413)
        plt.plot(seasonal,label='Seasonality', color='blue')
        plt.legend(loc='best')
        plt.subplot(414)
        plt.plot(residual, label='Residuals', color='blue')
        plt.legend(loc='best')
        plt.tight_layout()

    ts_decompose = residual
    ts_decompose.dropna(inplace=True)

    if check == True:
        check_stationarity(ts_decompose)
        return ""

    return ts_decompose

# Train-Test-Split function for a Time Series
def train_test_splt(ts,test_size):
    cutoff = int(ts.shape[0]*(1-test_size))
    train = ts[:cutoff]
    test = ts[cutoff:]
    return train, test

# Create a "Naive" Baseline
# One that is shifted by specified time step
def baseline_model(ts,shift,show=False):
    base = ts.shift(shift)

    if show == True:

        fig, ax = plt.subplots(figsize=(10,4))
        ax.set_title("Baseline Forecast")
        ax.plot(ts,c='b',label='Actual')
        ax.plot(base,c='r',label='Baseline')
        plt.legend()
        plt.show()
        return None
    return base

# Get all combinations
def get_combos(n,k):
    p = d = q = range(n, k)
    pdq = list(itertools.product(p, d, q))
    pdqs = [(x[0], x[1], x[2]) for x in list(itertools.product(p, d, q))]
    return pdqs

# Find optimal order for ARIMA model
def get_optimal_params(ts,n,k):
    pdq = get_combos(n,k)
    ans = []
    for comb in pdq:
        try:
            model = ARIMA(ts,
                         order=comb)
            output = model.fit()
            ans.append([comb,output.aic])
        except:
            continue
    ans_df = pd.DataFrame(ans, columns=['pdq','aic'])
    optimals = ans_df.loc[ans_df['aic'].idxmin()]
    return optimals

# Implement Arimal model using optimal order
def arima_model(ts,n,k):
    order = get_optimal_params(ts,n,k)['pdq']
    model = ARIMA(ts,
                 order=order)
    output = model.fit()
    return output
    
# RMSE function

def find_rmse(model, test_data):
    y_hat = model.predict(start=test_data.index[0], end=test_data.index[-1], typ='levels')
    return np.sqrt(mean_squared_error(test_data, y_hat))
