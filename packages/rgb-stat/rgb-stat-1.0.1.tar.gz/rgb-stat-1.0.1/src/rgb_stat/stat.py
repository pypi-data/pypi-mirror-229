"""Stat functions."""

from typing import List
import numpy as np
from scipy import stats


def _set_stat(
        stat: int | float | List[int|float],
        ct: dict,
        name: str,
        i: int) -> None:
    if isinstance(stat, np.uint8):
        stat = int(stat)
    
    if isinstance(stat, np.float64):
        stat = float(
            np.round(stat, 4)
        )

    if isinstance(stat, list):
        for j, stat_x in enumerate(stat):
            if isinstance(stat_x, np.float64):
                stat[j] = float(
                    np.round(stat_x, 4)
                )

    ct["stat"][i][name] = stat


def mean(data, ct):
    for i, color in enumerate(data):
        _set_stat(
            np.mean(color), ct, "mean", i)


def median(data, ct):
    for i, color in enumerate(data):
        _set_stat(
            np.median(color), ct, "median", i)


def maximum(data, ct):
    for i, color in enumerate(data):
        _set_stat(
            np.max(color), ct, "max", i)


def minimum(data, ct):
    for i, color in enumerate(data):
        _set_stat(
            np.min(color), ct, "min", i)


def var(data, ct):
    for i, color in enumerate(data):
        _set_stat(np.var(color, ddof=1), ct, "var", i)


def sig_test(ct, im_ct):
    is_accurate = True

    for i, stat in enumerate(ct["stat"]):
        im_stat = im_ct["stat"][i]
        bottom, top = stat["confidence_int"]

        if im_stat["mean"] < bottom or im_stat["mean"] > top:
            is_accurate = False
        
        _set_stat(is_accurate, im_ct, "is_accurate", i)


def std_error(data, ct):
    for i, color in enumerate(data):
        n = len(color)
        _set_stat(
            np.std(color) / np.sqrt(n), ct, "std_error", i
        )


def confidence_test(data, ct, alpha):
    for i, color in enumerate(data):
        stat = ct["stat"][i]
        n = len(color)
        bottom = stats.t.ppf(
            alpha / 2, df=n - 1,
            loc=stat["mean"], scale=stat["std_error"])
        top = stats.t.ppf(
            1 - alpha / 2, df=n - 1,
            loc=stat["mean"], scale=stat["std_error"])

        _set_stat([bottom, top], ct, "confidence_int", i)
