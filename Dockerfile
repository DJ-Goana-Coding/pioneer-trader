FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Force uvicorn to bind to the Render PORT
CMD ["python", "backend/main.py"]