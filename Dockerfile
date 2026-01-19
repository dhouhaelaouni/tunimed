FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- MINIMAL CHANGE START ---
# Instead of COPY . ., copy only the existing folders and app.py
COPY app.py .
COPY models/ ./models/
COPY resources/ ./resources/
COPY services/ ./services/
COPY utils/ ./utils/
COPY decorators/ ./decorators/
# --- MINIMAL CHANGE END ---

EXPOSE 5000

CMD ["python", "app.py"]
