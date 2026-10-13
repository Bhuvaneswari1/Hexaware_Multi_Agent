FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --create-home trainer && mkdir -p /app/runtime && chown -R trainer:trainer /app
USER trainer
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1
CMD ["python", "-m", "uvicorn", "hour_05_evaluation_deployment.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
