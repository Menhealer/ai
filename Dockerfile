FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY src /app/src
COPY logs /app/logs
COPY .env .env.ai

EXPOSE 8010

CMD ["uvicorn", "src.serving.api:app", "--host", "0.0.0.0", "--port", "8010"]
