FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY reporting_app.py .
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn","reporting_app:app","--host","0.0.0.0","--port","8001","--workers","1"]
