# ---- Stage 1: Builder ----
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Production ----
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN mkdir -p /app/staticfiles /app/media \
    && chown -R appuser:appgroup /app \
    && chmod -R 755 /app/staticfiles /app/media

USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]