import io
from typing import List, Tuple

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller


def ticks_to_df(rows: List[Tuple[int, str, float, float]]):
    # rows: list of (ts, symbol, price, qty)
    if not rows:
        return pd.DataFrame(columns=["ts", "symbol", "price", "qty"]).astype({"ts":"int64"})
    df = pd.DataFrame(rows, columns=["ts", "symbol", "price", "qty"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    return df


def resample_ohlc(df: pd.DataFrame, symbol: str, rule: str = "1s"):
    d = df[df["symbol"] == symbol].set_index("ts")["price"].resample(rule).ohlc()
    return d.dropna()


def compute_ols_hedge(y: pd.Series, x: pd.Series):
    # regress y = a + b*x
    df = pd.concat([y, x], axis=1).dropna()
    if df.shape[0] < 2:
        return None
    X = np.vstack([np.ones(len(df)), df.iloc[:,1].values]).T
    yv = df.iloc[:,0].values
    b, residuals, rank, s = np.linalg.lstsq(X, yv, rcond=None)
    a, beta = b[0], b[1]
    fitted = a + beta * df.iloc[:,1].values
    spread = df.iloc[:,0].values - fitted
    return {
        "intercept": float(a),
        "beta": float(beta),
        "spread_series": pd.Series(spread, index=df.index),
        "residuals": residuals,
    }


def rolling_zscore(series: pd.Series, window: int = 60):
    mu = series.rolling(window=window).mean()
    sigma = series.rolling(window=window).std()
    return (series - mu) / sigma


def run_adf(series: pd.Series):
    series = series.dropna()
    if len(series) < 10:
        return None
    res = adfuller(series.values)
    return {
        "adf_stat": float(res[0]),
        "pvalue": float(res[1]),
        "usedlag": int(res[2]),
        "nobs": int(res[3]),
        "critical": {k: float(v) for k, v in res[4].items()},
    }


def df_to_csv_bytes(df: pd.DataFrame):
    buf = io.StringIO()
    df.to_csv(buf, index=True)
    return buf.getvalue().encode()


if __name__ == "__main__":
    import pandas as pd
    print('analytics module loaded')
