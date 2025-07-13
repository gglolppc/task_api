FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

COPY dockerized_app/ .

RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "app.py"]
