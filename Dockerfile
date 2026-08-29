FROM python:3.11-slim AS backend

# System deps for OpenCV, Tesseract, and audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-eng \
    libgl1-mesa-glx libglib2.0-0 \
    ffmpeg libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cache layer)
COPY pyproject.toml .
RUN pip install --no-cache-dir \
    fastapi uvicorn httpx pydantic numpy pandas \
    scikit-learn scipy opencv-python-headless \
    cryptography aiofiles aiohttp requests \
    websockets psutil ollama mediapipe PyYAML \
    gTTS SpeechRecognition joblib piper-tts || true

# Copy source code & pre-trained model
COPY *.py ./
COPY wesad_model.joblib ./
COPY medical_rag.py ./
COPY fhir_exporter.py ./
COPY baymax_service.py ./
COPY cds_hooks.py ./
COPY sih_evaluator.py ./
COPY train_wesad_model.py ./
COPY data/ ./data/
COPY config/ ./config/

# Create runtime dirs
RUN mkdir -p var/db var/logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/status || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
