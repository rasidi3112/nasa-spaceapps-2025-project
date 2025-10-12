# Gunakan Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Salin requirements
COPY requirements.txt .

# Install dependencies dengan timeout lebih tinggi dan retry
RUN pip install --no-cache-dir --default-timeout=100 --retries=5 -r requirements.txt \
    -i https://pypi.org/simple

# Salin seluruh source code
COPY . .

# Jalankan FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
