FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ingestion_app.py .
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn","ingestion_app:app","--host","0.0.0.0","--port","8000","--workers","1"]
