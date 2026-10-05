"""Backend de inferência: carrega o artefato treinado e expõe predições via HTTP."""
import json
import os
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import List, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from common.features import WINDOW, build_features

MODEL_DIR = os.getenv("MODEL_DIR", "models")
DATA_PATH = os.getenv("DATA_PATH", "data/btc_usd_daily.csv")

state = {"model": None, "metadata": None}


def load_model():
    model_path = os.path.join(MODEL_DIR, "model.joblib")
    state["model"] = joblib.load(model_path)
    with open(os.path.join(MODEL_DIR, "metadata.json"), encoding="utf-8") as f:
        state["metadata"] = json.load(f)
    print(f"[startup] modelo '{state['metadata']['model_name']}' carregado de {model_path}")


@asynccontextmanager
async def lifespan(_app):
    load_model()
    yield


app = FastAPI(title="BTC-USD Predictor", version="1.0.0", lifespan=lifespan)


class PredictRequest(BaseModel):
    closes: List[float] = Field(..., description=f"Últimos fechamentos diários em ordem cronológica (mín. {WINDOW + 1})")
    last_date: Optional[str] = Field(None, description="Data (YYYY-MM-DD) do último fechamento enviado")


def predict_from_closes(closes: List[float]) -> dict:
    if len(closes) < WINDOW + 1:
        raise HTTPException(422, f"Envie pelo menos {WINDOW + 1} fechamentos (recebido {len(closes)}).")
    if any(c <= 0 for c in closes):
        raise HTTPException(422, "Todos os preços devem ser positivos.")
    series = pd.Series(closes, dtype=float)
    x = build_features(series).iloc[[-1]]
    pred_ret = float(state["model"].predict(x)[0])
    last_close = float(series.iloc[-1])
    return {
        "last_close": round(last_close, 2),
        "predicted_log_return": round(pred_ret, 6),
        "predicted_change_pct": round((np.exp(pred_ret) - 1) * 100, 4),
        "predicted_next_close": round(last_close * np.exp(pred_ret), 2),
        "model": state["metadata"]["model_name"],
        "disclaimer": "Predição experimental; não é recomendação de investimento.",
    }


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": state["model"] is not None}


@app.get("/model")
def model_info():
    return state["metadata"]


@app.post("/predict")
def predict(req: PredictRequest):
    result = predict_from_closes(req.closes)
    if req.last_date:
        result["last_date"] = req.last_date
        result["target_date"] = str((pd.Timestamp(req.last_date) + timedelta(days=1)).date())
    return result


@app.get("/predict/latest")
def predict_latest():
    """Usa o CSV (banco de dados) para prever o dia seguinte ao último registro."""
    df = pd.read_csv(DATA_PATH, parse_dates=["date"]).sort_values("date")
    tail = df.tail(WINDOW + 1)
    result = predict_from_closes(tail["close"].tolist())
    last_date = tail["date"].iloc[-1]
    result["last_date"] = str(last_date.date())
    result["target_date"] = str((last_date + timedelta(days=1)).date())
    return result
