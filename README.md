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

---

## 🚀 Quick Start

### Prerequisites

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

### Installation

**1. Clone the repository:**

```bash
git clone https://github.com/masasibata/t-one-rest-api.git
cd t-one-rest-api
```

**2. Install dependencies:**

```bash
make install
```

This command will:

- ✅ Check for required system dependencies (cmake)
- ✅ Clone the T-one repository automatically
- ✅ Install Poetry (if not already installed)
- ✅ Install all Python dependencies including T-one

> ⏱️ **Note:** Installation may take several minutes when building the `kenlm` package. Be patient!

**3. Start the server:**

```bash
make run
```

**4. Access the API:**

- 🌐 API: `http://localhost:8000`
- 📖 Swagger UI: `http://localhost:8000/docs`
- 📘 ReDoc: `http://localhost:8000/redoc`

---

## 📖 API Documentation

### Interactive Documentation

Once the server is running, you can explore the API using:

- **Swagger UI** (`/docs`) - Interactive API explorer with "Try it out" feature
- **ReDoc** (`/redoc`) - Beautiful, responsive API documentation

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

**Example Request:**

```bash
curl -X POST "http://localhost:8000/transcribe/streaming/chunk" \
     -F "state_id=550e8400-e29b-41d4-a716-446655440000" \
     -F "file=@chunk.wav"
```

### `POST /transcribe/streaming/finalize` - Finalize Streaming

Finalize streaming session and get final results.

**Parameters:**

- `state_id` (string, required) - State ID from streaming session

**Example Request:**

```bash
curl -X POST "http://localhost:8000/transcribe/streaming/finalize" \
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

# 1. Start streaming session
response = requests.post("http://localhost:8000/transcribe/streaming")
state_id = response.json()["state_id"]

# 2. Process audio chunks
chunk_files = ["chunk1.wav", "chunk2.wav", "chunk3.wav"]

for chunk_file in chunk_files:
    with open(chunk_file, "rb") as f:
        response = requests.post(
            "http://localhost:8000/transcribe/streaming/chunk",
            files={"file": f},
            data={"state_id": state_id}
        )
        result = response.json()

        # Print recognized phrases
        for phrase in result["phrases"]:
            print(f"{phrase['start_time']:.2f}s - {phrase['end_time']:.2f}s: {phrase['text']}")

# 3. Finalize session
response = requests.post(
    "http://localhost:8000/transcribe/streaming/finalize",
    data={"state_id": state_id}
)
final_result = response.json()
print("\nFinal phrases:")
for phrase in final_result["phrases"]:
    print(f"{phrase['start_time']:.2f}s - {phrase['end_time']:.2f}s: {phrase['text']}")
```

> 📝 See `asr_api/example_client.py` for a complete working example.

---

## 🛠️ Makefile Commands

| Command        | Description                              |
| -------------- | ---------------------------------------- |
| `make install` | Clone T-one and install all dependencies |
| `make run`     | Start the ASR API server                 |
| `make clean`   | Remove T-one clone and cache files       |
| `make help`    | Show available commands                  |

---

## 🔧 Alternative Installation

If you prefer to install manually without Makefile:

```bash
# 1. Clone T-one repository
git clone https://github.com/voicekit-team/T-one.git

# 2. Install with Poetry
poetry install

# 3. Run the server
poetry run uvicorn asr_api.main:app --host 0.0.0.0 --port 8000 --reload
```

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

1. **State Storage** - Replace in-memory `streaming_states` with Redis for multi-instance deployment
2. **CORS** - Configure specific domains instead of `"*"` in `CORSMiddleware`
3. **Authentication** - Add JWT tokens or API keys to protect endpoints
4. **Rate Limiting** - Implement request rate limiting per client
5. **Logging** - Set up centralized logging (ELK, Loki, etc.)
6. **Monitoring** - Add metrics (Prometheus/Grafana)
7. **Reverse Proxy** - Use nginx for load balancing and SSL
8. **File Size Limits** - Configure maximum file size restrictions

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
