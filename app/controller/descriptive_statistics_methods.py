import numpy as np
import scipy.stats as stats


def mean(data: list):
    return np.mean(data)


def mode(data: list):
    mode_result = stats.mode(data, nan_policy='omit')
    return mode_result.mode[0] if mode_result.count[0] > 0 else None


def median(data: list):
    return np.median(data)


def standard_deviation(data: list):
    return np.std(data, ddof=1)  # Bessel's correction


def skewness(data):
    return stats.skew(data, bias=False)


def kurtosis(data: list):
    return stats.kurtosis(data, fisher=False, bias=False)  # нормальна = 3


def jarque_bera_statistics(data: list):
    jb_stat, p_value = stats.jarque_bera(data)
    return {
        "jb_statistic": jb_stat,
        "p_value": p_value,
        "normality": p_value > 0.05  # True if distribution is likely normal
    }


def descriptive_statistics(data: list):
    return {
        "mean": mean(data),
        "mode": mode(data),
        "median": median(data),
        "standard_deviation": standard_deviation(data),
        "skewness": skewness(data),
        "kurtosis": kurtosis(data),
        "jarque_bera_statistics": jarque_bera_statistics(data),
    }
