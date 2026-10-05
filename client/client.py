"""Aplicação cliente: lê o histórico do CSV, chama o backend e exibe a predição."""
import csv
import os
import sys

import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")
DATA_PATH = os.getenv("DATA_PATH", "data/btc_usd_daily.csv")
N_CLOSES = 31


def main():
    health = requests.get(f"{API_URL}/health", timeout=5).json()
    print(f"[health] {health}")
    if health.get("status") != "ok":
        sys.exit("Backend indisponível")

    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))[-N_CLOSES:]
    closes = [float(r["close"]) for r in rows]
    payload = {"closes": closes, "last_date": rows[-1]["date"]}
    print(f"[request] POST {API_URL}/predict com {len(closes)} fechamentos "
          f"({rows[0]['date']} -> {rows[-1]['date']})")

    resp = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
    resp.raise_for_status()
    r = resp.json()
    print(f"[response] {r}")
    print(f"\nBTC-USD em {r['last_date']}: ${r['last_close']:,.2f}")
    print(f"Previsão para {r['target_date']}: ${r['predicted_next_close']:,.2f} "
          f"({r['predicted_change_pct']:+.3f}%) [modelo: {r['model']}]")


if __name__ == "__main__":
    main()
