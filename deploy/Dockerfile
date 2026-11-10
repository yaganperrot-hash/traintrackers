# Image unique : collecte (poc/collect.py) et ingestion (backend.ingestion). Contexte = racine du dépôt.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY pytest.ini ./
COPY backend/ backend/
COPY tests/ tests/
COPY poc/collect.py poc/analyse.py poc/regions.py poc/
ENV PYTHONUNBUFFERED=1
