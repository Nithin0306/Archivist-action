FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY entrypoint.py .

# GitHub Actions overrides the entrypoint, but this sets the default command
ENTRYPOINT ["python", "/app/entrypoint.py"]