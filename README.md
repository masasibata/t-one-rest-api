# 🎤 T-one REST API

> A production-ready REST API for Russian speech recognition using the [T-one](https://huggingface.co/t-tech/T-one) model

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Poetry](https://img.shields.io/badge/Poetry-2.1+-orange.svg)](https://python-poetry.org/)

A complete, ready-to-use REST API that provides Russian speech recognition capabilities. Simply clone, install, and run!

---

## ✨ Features

- 🎯 **Offline Recognition** - Transcribe complete audio files with timestamps
- 🔄 **Streaming Recognition** - Real-time speech recognition with low latency
- 📚 **Auto Documentation** - Interactive Swagger UI and ReDoc
- 🚀 **Easy Setup** - Automated installation with Makefile
- 🏭 **Production Ready** - Clean codebase with comprehensive error handling
- 🌐 **RESTful API** - Standard HTTP endpoints for easy integration
- 🔴 **Redis Support** - Optional Redis storage for multi-instance deployments
- 🐳 **Docker Support** - Ready-to-use Docker images and docker-compose setup

---

## 🚀 Quick Start

Choose your preferred deployment method:

### 🐳 Option 1: Docker (Recommended - Fastest)

The easiest way to get started is using Docker Compose. No need to install dependencies manually!

**With Memory Storage:**

```bash
# Clone repository
git clone https://github.com/masasibata/t-one-rest-api.git
cd t-one-rest-api

# Start API (builds automatically on first run)
docker compose up -d api

# View logs
docker compose logs -f api
```

**With Redis Storage (for production):**

```bash
# Start API with Redis
docker compose up -d api-redis redis

# View logs
docker compose logs -f api-redis
```

**Access the API:**

- 🌐 API: `http://localhost:8000` (memory) or `http://localhost:8001` (Redis)
- 📖 Swagger UI: `http://localhost:8000/docs`
- 📘 ReDoc: `http://localhost:8000/redoc`

> 💡 **Tip:** Docker automatically handles all dependencies, model downloads, and configuration. Perfect for quick testing and production deployment!

### 🔧 Option 2: Local Installation

For development or if you prefer local installation:

**Prerequisites:**

| Requirement | Version | Installation                          |
| ----------- | ------- | ------------------------------------- |
| Python      | 3.9+    | [python.org](https://www.python.org/) |
| Poetry      | 2.1+    | Auto-installed by Makefile            |
| Git         | Latest  | [git-scm.com](https://git-scm.com/)   |
| cmake       | 3.10+   | See below                             |
| Build Tools | -       | See below                             |

**Install cmake and build tools:**

```bash
# Ubuntu/Debian
sudo apt-get install cmake build-essential

# macOS
brew install cmake
xcode-select --install

# Windows
# Download from https://cmake.org/download/
```

**Installation Steps:**

1. **Clone the repository:**

```bash
git clone https://github.com/masasibata/t-one-rest-api.git
cd t-one-rest-api
```

2. **Install dependencies:**

```bash
make install
```

This command will:

- ✅ Check for required system dependencies (cmake)
- ✅ Clone the T-one repository automatically
- ✅ Install Poetry (if not already installed)
- ✅ Install all Python dependencies including T-one

> ⏱️ **Note:** Installation may take several minutes when building the `kenlm` package. Be patient!

3. **(Optional) Install with Redis support:**

For production deployments with multiple API instances:

```bash
make install-redis
```

> 💡 **Note:** For single-instance deployments, the default memory storage is sufficient.

4. **Start the server:**

```bash
make run
```

5. **Access the API:**

- 🌐 API: `http://localhost:8000`
- 📖 Swagger UI: `http://localhost:8000/docs`
- 📘 ReDoc: `http://localhost:8000/redoc`

---

## 📖 API Documentation

### Interactive Documentation

Once the server is running, you can explore the API using:

- **Swagger UI** (`/docs`) - Interactive API explorer with "Try it out" feature (protected with `X-API-Key` header if `API_KEY` is set)
- **ReDoc** (`/redoc`) - Beautiful, responsive API documentation (protected with `X-API-Key` header if `API_KEY` is set)

### API Authentication (Optional)

The API supports optional API key authentication. If `API_KEY` environment variable is set, all endpoints except `/health` and `/` require the key to be provided in the `X-API-Key` header.

**Configuration:**

```bash
# Set API key via environment variable
export API_KEY=your-secret-key-here

# Or in .env file
echo "API_KEY=your-secret-key-here" >> .env
```

**Usage:**

When API key is configured, include it in the `X-API-Key` header:

```bash
# Without API key (if not configured)
curl -X POST "http://localhost:8000/transcribe" -F "file=@audio.wav"

# With API key (if configured)
curl -X POST "http://localhost:8000/transcribe" \
     -H "X-API-Key: your-secret-key-here" \
     -F "file=@audio.wav"
```

**Protected Endpoints:**

- `POST /transcribe` - Requires API key if configured
- `POST /transcribe/streaming` - Requires API key if configured
- `POST /transcribe/streaming/chunk` - Requires API key if configured
- `POST /transcribe/streaming/finalize` - Requires API key if configured

**Public Endpoints (always accessible):**

- `GET /` - API information
- `GET /health` - Health check

**Protected Documentation (if `API_KEY` is set):**

- `GET /docs` - Swagger UI (requires `X-API-Key` header)
- `GET /redoc` - ReDoc documentation (requires `X-API-Key` header)

> 💡 **Note:** If `API_KEY` is not set, the API works without authentication. This is useful for development or internal networks.

### Endpoints Overview

| Method | Endpoint                         | Description                              |
| ------ | -------------------------------- | ---------------------------------------- |
| `GET`  | `/`                              | API information and available endpoints  |
| `GET`  | `/health`                        | Health check and model status            |
| `POST` | `/transcribe`                    | Transcribe complete audio file (offline) |
| `POST` | `/transcribe/streaming`          | Start streaming recognition session      |
| `POST` | `/transcribe/streaming/chunk`    | Process audio chunk in streaming mode    |
| `POST` | `/transcribe/streaming/finalize` | Finalize streaming session               |

---

## 🔌 API Endpoints

### `GET /` - API Information

Get information about the API and available endpoints.

**Response:**

```json
{
  "name": "T-one ASR API",
  "version": "1.0.0",
  "description": "REST API for Russian speech recognition",
  "endpoints": {
    "POST /transcribe": "Transcribe speech from audio file (offline)",
    "POST /transcribe/streaming": "Start streaming recognition",
    "POST /transcribe/streaming/chunk": "Send audio chunk for streaming",
    "POST /transcribe/streaming/finalize": "Finalize streaming"
  }
}
```

### `GET /health` - Health Check

Check API status and verify model is loaded.

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### `POST /transcribe` - Offline Recognition

Transcribe speech from a complete audio file.

**Parameters:**

- `file` (file, required) - Audio file (WAV, FLAC, MP3, OGG, etc.)
- `return_timestamps` (bool, optional) - Return timestamps with phrases (default: `true`)

**Example Request:**

```bash
curl -X POST "http://localhost:8000/transcribe" \
     -F "file=@audio.wav" \
     -F "return_timestamps=true"
```

**Example Response:**

```json
{
  "phrases": [
    {
      "text": "привет",
      "start_time": 1.79,
      "end_time": 2.04
    },
    {
      "text": "это тест",
      "start_time": 3.72,
      "end_time": 4.26
    }
  ],
  "full_text": "привет это тест",
  "duration": 4.26,
  "processing_time": 0.85
}
```

### `POST /transcribe/streaming` - Start Streaming

Create a new streaming recognition session.

**Headers:**

- `X-API-Key` (string, optional) - API key for authentication (required if `API_KEY` env var is set)

**Example Request:**

```bash
# Without API key (if not configured)
curl -X POST "http://localhost:8000/transcribe/streaming"

# With API key (if configured)
curl -X POST "http://localhost:8000/transcribe/streaming" \
     -H "X-API-Key: your-secret-key"
```

**Response:**

```json
{
  "phrases": [],
  "state_id": "550e8400-e29b-41d4-a716-446655440000",
  "is_final": false
}
```

### `POST /transcribe/streaming/chunk` - Process Chunk

Process an audio chunk in streaming mode.

**Parameters:**

- `state_id` (string, required) - State ID from `/transcribe/streaming`
- `file` (file, required) - Audio chunk

**Headers:**

- `X-API-Key` (string, optional) - API key for authentication (required if `API_KEY` env var is set)

**Example Request:**

```bash
# Without API key (if not configured)
curl -X POST "http://localhost:8000/transcribe/streaming/chunk" \
     -F "state_id=550e8400-e29b-41d4-a716-446655440000" \
     -F "file=@chunk.wav"

# With API key (if configured)
curl -X POST "http://localhost:8000/transcribe/streaming/chunk" \
     -H "X-API-Key: your-secret-key" \
     -F "state_id=550e8400-e29b-41d4-a716-446655440000" \
     -F "file=@chunk.wav"
```

### `POST /transcribe/streaming/finalize` - Finalize Streaming

Finalize streaming session and get final results.

**Parameters:**

- `state_id` (string, required) - State ID from streaming session

**Headers:**

- `X-API-Key` (string, optional) - API key for authentication (required if `API_KEY` env var is set)

**Example Request:**

```bash
# Without API key (if not configured)
curl -X POST "http://localhost:8000/transcribe/streaming/finalize" \
     -F "state_id=550e8400-e29b-41d4-a716-446655440000"

# With API key (if configured)
curl -X POST "http://localhost:8000/transcribe/streaming/finalize" \
     -H "X-API-Key: your-secret-key" \
     -F "state_id=550e8400-e29b-41d4-a716-446655440000"
```

---

## 💻 Usage Examples

### Python Example - Offline Recognition

```python
import requests

# Transcribe audio file
with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/transcribe",
        files={"file": f},
        data={"return_timestamps": True}
    )
    result = response.json()

    print(f"Full text: {result['full_text']}")
    print(f"Processing time: {result['processing_time']:.2f} sec")

    for phrase in result["phrases"]:
        print(f"{phrase['start_time']:.2f}s - {phrase['end_time']:.2f}s: {phrase['text']}")
```

### Python Example - Streaming Recognition

```python
import requests
import os

# Optional: Get API key from environment
api_key = os.getenv("API_KEY")
headers = {"X-API-Key": api_key} if api_key else {}

# 1. Start streaming session
response = requests.post(
    "http://localhost:8000/transcribe/streaming",
    headers=headers
)
state_id = response.json()["state_id"]

# 2. Process audio chunks
chunk_files = ["chunk1.wav", "chunk2.wav", "chunk3.wav"]

for chunk_file in chunk_files:
    with open(chunk_file, "rb") as f:
        response = requests.post(
            "http://localhost:8000/transcribe/streaming/chunk",
            files={"file": f},
            data={"state_id": state_id},
            headers=headers
        )
        result = response.json()

        # Print recognized phrases
        for phrase in result["phrases"]:
            print(f"{phrase['start_time']:.2f}s - {phrase['end_time']:.2f}s: {phrase['text']}")

# 3. Finalize session
response = requests.post(
    "http://localhost:8000/transcribe/streaming/finalize",
    data={"state_id": state_id},
    headers=headers
)
final_result = response.json()
print("\nFinal phrases:")
for phrase in final_result["phrases"]:
    print(f"{phrase['start_time']:.2f}s - {phrase['end_time']:.2f}s: {phrase['text']}")
```

> 📝 See `asr_api/example_client.py` for a complete working example.

---

## 🛠️ Makefile Commands

| Command              | Description                                        |
| -------------------- | -------------------------------------------------- |
| `make install`       | Clone T-one and install dependencies (memory)      |
| `make install-redis` | Install with Redis support for distributed storage |
| `make run`           | Start the ASR API server                           |
| `make docker-build`  | Build Docker images                                |
| `make docker-up`     | Start services with docker-compose                 |
| `make docker-down`   | Stop docker-compose services                       |
| `make docker-logs`   | View docker-compose logs                           |
| `make clean`         | Remove T-one clone and cache files                 |
| `make help`          | Show available commands                            |

---

## 🐳 Docker Deployment Details

### Docker Compose Services

The `docker-compose.yml` includes three services:

| Service     | Description             | Port | Storage   |
| ----------- | ----------------------- | ---- | --------- |
| `api`       | API with memory storage | 8000 | In-memory |
| `api-redis` | API with Redis storage  | 8001 | Redis     |
| `redis`     | Redis server            | 6379 | -         |

### Quick Commands

```bash
# Start API with memory storage
docker compose up -d api

# Start API with Redis
docker compose up -d api-redis redis

# View logs
docker compose logs -f api

# Stop all services
docker compose down

# Rebuild images
docker compose build
```

### Manual Docker Build

If you prefer to build and run manually:

**Build images:**

```bash
# Memory storage version
docker build -t t-one-rest-api .

# Redis version
docker build -f Dockerfile.redis -t t-one-rest-api:redis .
```

**Run containers:**

```bash
# Memory storage
docker run -d \
  --name t-one-api \
  -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  t-one-rest-api

# Redis storage (requires Redis running)
docker run -d \
  --name t-one-api-redis \
  -p 8000:8000 \
  -e STORAGE_TYPE=redis \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  t-one-rest-api:redis
```

### Configuration

**Environment Variables:**

| Variable                  | Default                    | Description                                 |
| ------------------------- | -------------------------- | ------------------------------------------- |
| `HOST`                    | `0.0.0.0`                  | Server host                                 |
| `PORT`                    | `8000`                     | Server port                                 |
| `LOG_LEVEL`               | `INFO`                     | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `STORAGE_TYPE`            | `memory`                   | Storage type: `memory` or `redis`           |
| `REDIS_URL`               | `redis://localhost:6379/0` | Redis connection URL                        |
| `REDIS_KEY_PREFIX`        | `asr:session:`             | Redis key prefix                            |
| `SESSION_TIMEOUT_SECONDS` | `3600`                     | Session timeout in seconds                  |
| `MAX_FILE_SIZE_MB`        | `100`                      | Maximum file size in MB                     |
| `API_KEY`                 | `None` (optional)          | Optional API key for authentication         |

**Volumes:**

- `model-cache` - Caches downloaded models from HuggingFace (persists between restarts)
- `redis-data` - Persistent Redis data storage

**Health Checks:**

All services include automatic health checks:

- API: `GET /health` endpoint
- Redis: `redis-cli ping` command

---

## 🔴 Redis Storage (Optional)

For production deployments with multiple API instances or when you need persistent session storage, you can use Redis instead of in-memory storage.

### Installation with Redis

```bash
# Install with Redis support
make install-redis
```

Or manually:

```bash
poetry install --extras redis
```

### Configuration

Set environment variables to use Redis:

```bash
export STORAGE_TYPE=redis
export REDIS_URL=redis://localhost:6379/0
export REDIS_KEY_PREFIX=asr:session:
```

Or create a `.env` file:

```env
STORAGE_TYPE=redis
REDIS_URL=redis://localhost:6379/0
REDIS_KEY_PREFIX=asr:session:
```

### Running Redis

**Docker (recommended):**

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

**Local installation:**

```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

### When to Use Redis

- ✅ **Multi-instance deployments** - Share sessions across multiple API servers
- ✅ **High availability** - Sessions survive server restarts
- ✅ **Horizontal scaling** - Load balance requests across instances
- ✅ **Production environments** - Better reliability and monitoring

- ❌ **Single instance** - Memory storage is simpler and faster
- ❌ **Development/testing** - No need for additional infrastructure
- ❌ **Low traffic** - Memory storage is sufficient

### Storage Comparison

| Feature              | Memory Storage       | Redis Storage           |
| -------------------- | -------------------- | ----------------------- |
| **Setup**            | No additional setup  | Requires Redis server   |
| **Performance**      | Fastest (in-process) | Fast (network overhead) |
| **Persistence**      | Lost on restart      | Survives restarts       |
| **Multi-instance**   | ❌ Not supported     | ✅ Supported            |
| **Scalability**      | Single server only   | Horizontal scaling      |
| **Production Ready** | Limited              | ✅ Recommended          |

---

## 🐛 Troubleshooting

### Network Timeout Errors

If you see `TimeoutError` or `Read timed out` during installation:

```bash
# Simply retry the installation
make install
```

### kenlm Installation Fails

If `kenlm` fails to install repeatedly:

```bash
# Install kenlm separately
poetry run pip install kenlm
poetry install
```

### Missing Build Tools

If you get compilation errors:

```bash
# Ubuntu/Debian
sudo apt-get install build-essential cmake

# macOS
xcode-select --install
brew install cmake
```

### Model Loading Issues

If the model fails to load on startup:

- Check your internet connection
- Verify DNS resolution: `ping huggingface.co`
- Check firewall settings
- Review server logs for detailed error messages

---

## 📊 Model Information

| Property          | Value                             |
| ----------------- | --------------------------------- |
| **Model**         | T-one (71M parameters)            |
| **Architecture**  | Conformer (CTC-based)             |
| **Language**      | Russian                           |
| **Domain**        | Telephony (call center optimized) |
| **Quality (WER)** | 8.63% on call-center data         |
| **Model Size**    | ~71MB (auto-downloaded)           |
| **Latency**       | Low (optimized for real-time)     |

---

## 🎵 Supported Audio Formats

The API supports all audio formats that can be read by `librosa`/`soundfile`:

- ✅ WAV
- ✅ FLAC
- ✅ MP3
- ✅ OGG
- ✅ And more...

Audio is automatically converted to mono 8kHz format for processing.

---

## 📁 Project Structure

```
t-one-rest-api/
├── asr_api/                 # Main API package
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic data models
│   ├── audio_processor.py  # Audio processing & T-one integration
│   └── example_client.py    # Usage examples
├── T-one/                   # T-one repository (auto-cloned)
├── pyproject.toml           # Poetry configuration
├── Makefile                 # Build automation
└── README.md                # This file
```

---

## 🧑‍💻 Development

### Adding Dependencies

The project uses Poetry for dependency management:

```bash
# Add a new dependency
poetry add <package-name>

# Add a development dependency
poetry add --group dev <package-name>
```

### Running in Development Mode

The server runs with auto-reload enabled by default:

```bash
make run
# or
poetry run uvicorn asr_api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🚀 Production Deployment

### Recommendations

1. **State Storage** - Use Redis storage for multi-instance deployments:

   ```bash
   # Install with Redis
   make install-redis

   # Configure
   export STORAGE_TYPE=redis
   export REDIS_URL=redis://your-redis-host:6379/0
   ```

2. **CORS** - Configure specific domains instead of `"*"` in `CORSMiddleware`
3. **Authentication** - Add JWT tokens or API keys to protect endpoints
4. **Rate Limiting** - Implement request rate limiting per client
5. **Logging** - Set up centralized logging (ELK, Loki, etc.)
6. **Monitoring** - Add metrics (Prometheus/Grafana)
7. **Reverse Proxy** - Use nginx for load balancing and SSL
8. **File Size Limits** - Configure maximum file size restrictions (default: 100MB)

---

## 📄 License

This project is licensed under the **MIT License**.

The T-one model is licensed under the **Apache 2.0 License**.

---

## 🔗 Links

- 🎯 [T-one Model on HuggingFace](https://huggingface.co/t-tech/T-one)
- 📦 [T-one GitHub Repository](https://github.com/voicekit-team/T-one)
- 📚 [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 🐍 [Poetry Documentation](https://python-poetry.org/docs/)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Made with ❤️ for Russian speech recognition**
