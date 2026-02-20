FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Remove start.sh dependence for direct ignition
EXPOSE 10000
CMD ["python", "main.py"]
