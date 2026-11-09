# Collecte du POC (jalon 1), image minimale. Les données vivent hors de l'image (volume data/).
FROM python:3.12-slim
WORKDIR /app/poc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY collect.py analyse.py regions.py ./
CMD ["python", "-u", "collect.py"]
