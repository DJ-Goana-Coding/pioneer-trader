FROM python:3.12-slim

WORKDIR /app

# Install system basics
RUN apt-get update && apt-get install -y git build-essential curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ship
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Expose the PROXY port only
EXPOSE 10000

# Launch
CMD ["./start.sh"]