FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Configure Poetry: Don't create virtual environment (we're in Docker)
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Clone T-one repository if not exists
RUN if [ ! -d "T-one" ]; then \
    git clone https://github.com/voicekit-team/T-one.git; \
    fi

# Install dependencies (without Redis by default)
RUN poetry install --no-interaction --no-root

# Download model during build (faster startup)
RUN echo "Downloading T-one model (this may take a few minutes)..." && \
    poetry run python -m tone download /models && \
    echo "Model downloaded successfully!"

# Copy application code
COPY asr_api/ ./asr_api/
COPY LICENSE ./

# Expose port
EXPOSE 8000

# Set environment variable to load model from local folder
ENV LOAD_FROM_FOLDER=/models

# Health check (using curl which is installed)
# Reduced start_period since model is pre-downloaded
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with unbuffered output
CMD ["poetry", "run", "python", "-u", "-m", "uvicorn", "asr_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

