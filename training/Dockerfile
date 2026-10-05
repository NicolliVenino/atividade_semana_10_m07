FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY training/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ ./common/
COPY training/train.py .

# /app/data  -> CSV (banco de dados), montado como volume somente leitura
# /app/models -> destino do artefato, volume compartilhado com o backend
CMD ["python", "train.py"]
