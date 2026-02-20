# Use a slim version to speed up build time
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for Pandas/CCXT
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from root to /app
COPY . .

# Force the PORT to be dynamic for Render
# Render provides the $PORT environment variable automatically
ENV PORT=10000
EXPOSE 10000

# Ignite the Citadel directly
CMD ["python", "main.py"]
