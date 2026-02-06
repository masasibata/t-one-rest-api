FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN if [ ! -d "T-one" ]; then \
    git clone https://github.com/voicekit-team/T-one.git; \
    fi

RUN poetry install --no-interaction --no-root

RUN --mount=type=cache,target=/root/.cache/huggingface \
    if [ ! -f /models/model.onnx ] || [ ! -f /models/kenlm.bin ]; then \
    echo "Downloading T-one model (this may take a few minutes)..." && \
    poetry run python -m tone download /models && \
    echo "Model downloaded successfully!"; \
    else \
    echo "Model already exists, skipping download."; \
    fi

COPY asr_api/ ./asr_api/
COPY LICENSE ./

EXPOSE 8000

ENV LOAD_FROM_FOLDER=/models
ENV WORKERS=1

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD poetry run gunicorn asr_api.main:app \
    -w ${WORKERS:-1} \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -

