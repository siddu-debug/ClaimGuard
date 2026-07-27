FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for C compilation if any
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code, scripts, and pre-trained models
COPY . .

# Train model during container build if model artifact does not exist
RUN python -c "from app.ml.train import train_fraud_model; train_fraud_model()"

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
