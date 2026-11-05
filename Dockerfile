FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code including prebuilt React frontend in frontend/dist
COPY . .

# Expose FastAPI port (8000) and Streamlit fallback (8501)
EXPOSE 8000 8501

# Default command: Runs the FastAPI server serving the React Terminal UI & WebSocket
CMD ["python", "src/api_server.py"]
