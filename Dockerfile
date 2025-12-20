FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port Hugging Face Spaces expects
EXPOSE 7860

# Run the application using the python script
CMD ["python", "run_app.py"]
