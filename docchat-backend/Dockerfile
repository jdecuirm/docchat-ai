FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (layer cached separately from app code)
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv export --no-hashes > requirements.txt && pip install -r requirements.txt

# Download HuggingFace models at build time so they live in the image layer.
# This avoids a ~5-minute cold-start download on every first request.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"
RUN python -c "from sentence_transformers import CrossEncoder; CrossEncoder('BAAI/bge-reranker-base')"

COPY . .

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
