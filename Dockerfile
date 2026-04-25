FROM python:3.14-slim

WORKDIR /app

# System deps (curl for healthchecks if needed; build essentials only if a wheel lacks)
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates tini \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps first to maximize layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir gunicorn

# Copy bot code + content
COPY bot.py config.py config.yaml ./
COPY channels/ ./channels/
COPY core/ ./core/
COPY content/ ./content/

# data/ is a mount point for the persistent SQLite db
RUN mkdir -p /app/data
VOLUME ["/app/data"]

# Bot listens on 8080 for WAHA webhooks
EXPOSE 8080

# tini reaps zombies & forwards signals cleanly
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-u", "bot.py"]
