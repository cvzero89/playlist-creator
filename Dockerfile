FROM python:3.12-slim

# Use env vars for runtime settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Install supercronic
ADD https://github.com/aptible/supercronic/releases/download/v0.2.33/supercronic-linux-amd64 /usr/local/bin/supercronic
RUN chmod +x /usr/local/bin/supercronic

# Set working dir and switch user
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY ./ /app/

# Create and set permissions for mountable config and assets directories
RUN mkdir -p /app/config /app/assets /app/logs /app/supercronic-config && chmod -R 775 /app/config /app/assets /app/logs /app/supercronic-config

# Specify mount points
VOLUME ["/app/config", "/app/assets", "/app/logs", "/app/supercronic-config"]

# Copy cron schedule and entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]