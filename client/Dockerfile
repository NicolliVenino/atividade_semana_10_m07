FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY client/client.py .
ENTRYPOINT ["python", "client.py"]
