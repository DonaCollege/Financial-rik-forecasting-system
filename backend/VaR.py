#VaR is Value at Risk - What is the max loss I can expect over a given time period at an X% confidence level
# e.g :- 1 day VaR at 95% = -2.3% = On 95% of the days, No more than 2.3% loss is expected.

import numpy as np
from scipy.stats import norm

def historical_var(returns, confidence = 0.95):  # High confidence means low VaR, 
    alpha = 1 - confidence
    return np.percentile(returns, alpha * 100)

def parametric_var(returns, confidence = 0.95):
    mu = returns.mean()
    sigma = returns.std()
    z = norm.ppf(1 - confidence)
    return mu + z * sigma 