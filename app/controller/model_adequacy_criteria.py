import numpy as np


def r_squared(y_true, y_pre):
    ss_total = np.var(y_true, ddof=1) * len(y_true)
    ss_reg = np.var(y_pre, ddof=1) * len(y_pre)
    return ss_reg / ss_total


def sum_square_resid(y_true, y_pre):
    return np.sum((y_true - y_pre) ** 2)


def durbin_watson(residuals):
    diff = np.diff(residuals)
    return np.sum(diff**2) / np.sum(residuals**2)


def aic(log_likelihood, n_obs, n_params):
    return -2 * log_likelihood + 2 * n_params


def bic(log_likelihood, n_obs, n_params):
    return -2 * log_likelihood + n_params * np.log(n_obs)


def sc(log_likelihood, n_obs, n_params):
    return -2 * log_likelihood + 2 * np.log(n_obs) * n_params


def t_statistic(coefficient, std_error):
    return coefficient / std_error


def mse(y_true, y_pre):
    return np.mean((y_true - y_pre) ** 2)


def mae(y_true, y_pre):
    return np.mean(np.abs(y_true - y_pre))
