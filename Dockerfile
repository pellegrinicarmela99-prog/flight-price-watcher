FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY flight_price_watcher.py .
ENV DB_PATH=/data/state.db
ENV TZ=America/Argentina/Buenos_Aires
CMD ["python","flight_price_watcher.py","--loop"]
