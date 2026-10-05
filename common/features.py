"""Engenharia de atributos compartilhada entre treinamento e inferência.

O mesmo código é copiado para as duas imagens Docker, garantindo que o
backend calcule os atributos exatamente como o treinamento calculou.
"""
import numpy as np
import pandas as pd

# Quantidade mínima de fechamentos necessária para montar uma linha de atributos
WINDOW = 30
LAGS = 7

FEATURE_NAMES = (
    [f"ret_lag_{i}" for i in range(1, LAGS + 1)]
    + ["ret_mean_7", "ret_mean_30", "vol_7", "vol_30", "close_sma7_ratio", "close_sma30_ratio"]
)


def build_features(close: pd.Series) -> pd.DataFrame:
    """Gera atributos a partir de uma série de preços de fechamento (ordem cronológica)."""
    close = close.astype(float)
    log_ret = np.log(close).diff()

    feats = pd.DataFrame(index=close.index)
    for i in range(1, LAGS + 1):
        feats[f"ret_lag_{i}"] = log_ret.shift(i - 1)
    feats["ret_mean_7"] = log_ret.rolling(7).mean()
    feats["ret_mean_30"] = log_ret.rolling(30).mean()
    feats["vol_7"] = log_ret.rolling(7).std()
    feats["vol_30"] = log_ret.rolling(30).std()
    feats["close_sma7_ratio"] = close / close.rolling(7).mean() - 1
    feats["close_sma30_ratio"] = close / close.rolling(30).mean() - 1
    return feats[FEATURE_NAMES]


def build_target(close: pd.Series) -> pd.Series:
    """Alvo: retorno logarítmico do dia seguinte (t -> t+1)."""
    return np.log(close.astype(float)).diff().shift(-1).rename("target_next_log_ret")
