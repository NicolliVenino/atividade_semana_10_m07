# Arquitetura (UML)

## Diagrama de componentes

Mostra os quatro componentes exigidos (ambiente de treinamento, artefato, container de inferência e aplicação cliente) e como o modelo chega ao container de inferência: pelo **volume compartilhado `./models`**.

```mermaid
flowchart LR
    subgraph HOST["Host (docker compose)"]
        CSV[("data/btc_usd_daily.csv<br/>«banco de dados»<br/>BTC-USD diário 2014-2026")]
        ART[["models/<br/>model.joblib<br/>metadata.json<br/>«artefato»"]]
    end

    subgraph TRAIN["«container» train<br/>python:3.12-slim"]
        T1[train.py] --> T2[common/features.py]
    end

    subgraph API["«container» api<br/>FastAPI + Uvicorn :8000"]
        A1[app.py] --> A2[common/features.py]
    end

    subgraph CLI["«container» client (profile client)"]
        C1[client.py]
    end

    USER((Usuário / curl / navegador))

    CSV -- "volume :ro" --> TRAIN
    TRAIN -- "joblib.dump()<br/>volume rw" --> ART
    ART -- "volume :ro<br/>joblib.load() no startup" --> API
    CSV -- "volume :ro<br/>(GET /predict/latest)" --> API
    CSV -- "volume :ro" --> CLI
    CLI -- "HTTP POST /predict<br/>(JSON: closes[])" --> API
    USER -- "HTTP GET /health<br/>GET /predict/latest<br/>GET /docs" --> API
```

## Diagrama de sequência

```mermaid
sequenceDiagram
    autonumber
    participant DC as docker compose
    participant TR as train (container)
    participant VOL as volume ./models
    participant API as api (container)
    participant CL as client (container)

    DC->>TR: up (1º serviço)
    TR->>TR: lê CSV, gera atributos, split cronológico
    TR->>TR: treina Ridge e GBR, compara com baseline ingênuo
    TR->>VOL: grava model.joblib + metadata.json
    TR-->>DC: exit 0 (service_completed_successfully)
    DC->>API: up (depends_on train)
    API->>VOL: joblib.load(model.joblib)
    API-->>DC: healthcheck GET /health = 200
    DC->>CL: run (depends_on api healthy)
    CL->>API: GET /health
    API-->>CL: {"status":"ok","model_loaded":true}
    CL->>API: POST /predict {closes: [31 valores], last_date}
    API->>API: build_features() + model.predict()
    API-->>CL: {predicted_next_close, predicted_change_pct, ...}
```

## Diagrama de classes / módulos (simplificado)

```mermaid
classDiagram
    class features {
        +WINDOW = 30
        +FEATURE_NAMES: list
        +build_features(close) DataFrame
        +build_target(close) Series
    }
    class train {
        +main()
        +price_metrics(close, true_ret, pred_ret) dict
    }
    class app {
        +GET /health
        +GET /model
        +POST /predict(PredictRequest)
        +GET /predict/latest
        -load_model()
        -predict_from_closes(closes) dict
    }
    class PredictRequest {
        +closes: List~float~
        +last_date: str?
    }
    class client {
        +main()
    }
    train ..> features : usa
    app ..> features : usa
    app ..> PredictRequest
    client ..> app : HTTP
```
