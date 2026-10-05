"""Treina um modelo para estimar o preço de fechamento do BTC-USD no dia seguinte.

Entrada : data/btc_usd_daily.csv (diário, Bitstamp via CryptoDataDownload)
Saída   : models/model.joblib  (pipeline scikit-learn)
          models/metadata.json (métricas, período, atributos)
"""
import json
import os
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from common.features import FEATURE_NAMES, WINDOW, build_features, build_target

DATA_PATH = os.getenv("DATA_PATH", "data/btc_usd_daily.csv")
MODEL_DIR = os.getenv("MODEL_DIR", "models")
START_DATE = os.getenv("START_DATE", "2018-01-01")
TEST_RATIO = float(os.getenv("TEST_RATIO", "0.2"))


def price_metrics(close_today, true_ret, pred_ret):
    """Converte retornos previstos em preço e calcula métricas em USD."""
    true_price = close_today * np.exp(true_ret)
    pred_price = close_today * np.exp(pred_ret)
    return {
        "mae_usd": round(float(mean_absolute_error(true_price, pred_price)), 2),
        "rmse_usd": round(float(np.sqrt(mean_squared_error(true_price, pred_price))), 2),
        "mape_pct": round(float(np.mean(np.abs(pred_price - true_price) / true_price) * 100), 4),
        # baseline ingênuo prevê retorno 0 (sem direção), então a métrica não se aplica
        "direction_acc_pct": None if not np.any(pred_ret) else round(float(np.mean(np.sign(pred_ret) == np.sign(true_ret)) * 100), 2),
    }


def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    print(f"[dados] {len(df)} linhas de {df.date.min().date()} a {df.date.max().date()}")

    feats = build_features(df["close"])
    target = build_target(df["close"])
    data = pd.concat([df[["date", "close"]], feats, target], axis=1)
    data = data[data.date >= START_DATE].dropna().reset_index(drop=True)

    # Divisão cronológica: nada de embaralhar uma série temporal
    split = int(len(data) * (1 - TEST_RATIO))
    train, test = data.iloc[:split], data.iloc[split:]
    print(f"[split] treino {train.date.min().date()} -> {train.date.max().date()} ({len(train)} linhas)")
    print(f"[split] teste  {test.date.min().date()} -> {test.date.max().date()} ({len(test)} linhas)")

    X_tr, y_tr = train[FEATURE_NAMES], train["target_next_log_ret"]
    X_te, y_te = test[FEATURE_NAMES], test["target_next_log_ret"]

    candidates = {
        "ridge": make_pipeline(StandardScaler(), Ridge(alpha=10.0)),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=200, max_depth=2, learning_rate=0.02, subsample=0.8, random_state=42
        ),
    }

    results = {"naive_last_close": price_metrics(test["close"].values, y_te.values, np.zeros(len(y_te)))}
    fitted = {}
    for name, model in candidates.items():
        model.fit(X_tr, y_tr)
        fitted[name] = model
        results[name] = price_metrics(test["close"].values, y_te.values, model.predict(X_te))

    print("[avaliação] métricas no conjunto de teste (preço do dia seguinte):")
    for name, m in results.items():
        print(f"  {name:<18} MAE=${m['mae_usd']:>9,.2f}  RMSE=${m['rmse_usd']:>9,.2f}  "
              f"MAPE={m['mape_pct']:.3f}%  acerto direção=" + (f"{m['direction_acc_pct']}%" if m['direction_acc_pct'] is not None else "n/a"))

    best = min(fitted, key=lambda n: results[n]["mae_usd"])
    print(f"[seleção] melhor modelo por MAE: {best}")

    # Re-treina o modelo escolhido com todo o histórico antes de exportar
    final_model = candidates[best].fit(data[FEATURE_NAMES], data["target_next_log_ret"])

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(final_model, os.path.join(MODEL_DIR, "model.joblib"))
    metadata = {
        "model_name": best,
        "target": "log-retorno do fechamento do dia seguinte; preço = close_hoje * exp(pred)",
        "asset": "BTC-USD",
        "frequency": "diária",
        "horizon_days": 1,
        "window": WINDOW,
        "features": FEATURE_NAMES,
        "train_period": [str(train.date.min().date()), str(train.date.max().date())],
        "final_fit_period": [str(data.date.min().date()), str(data.date.max().date())],
        "test_period": [str(test.date.min().date()), str(test.date.max().date())],
        "test_metrics": results,
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with open(os.path.join(MODEL_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"[export] {MODEL_DIR}/model.joblib e {MODEL_DIR}/metadata.json salvos")


if __name__ == "__main__":
    main()
