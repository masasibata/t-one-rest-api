.PHONY: install install-redis run clean help docker-build docker-up docker-down docker-logs

# Default target
help:
	@echo "Available targets:"
	@echo "  make install       - Clone T-One repository and install dependencies (memory storage)"
	@echo "  make install-redis - Install with Redis support for distributed storage"
	@echo "  make run           - Start the ASR API server"
	@echo "  make clean         - Remove T-One clone and cache files"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start services with docker-compose"
	@echo "  make docker-down   - Stop docker-compose services"
	@echo "  make docker-logs   - View docker-compose logs"

# Install dependencies (default: memory storage)
install:
	@echo "Installing T-one REST API (memory storage)..."
	@if ! command -v cmake > /dev/null 2>&1; then \
		echo "ERROR: cmake is required but not found."; \
		echo "Please install cmake first:"; \
		echo "  Ubuntu/Debian: sudo apt-get install cmake"; \
		echo "  macOS: brew install cmake"; \
		echo "  Or download from: https://cmake.org/download/"; \
		exit 1; \
	fi
	@if [ ! -d "T-one" ]; then \
		echo "Cloning T-One repository..."; \
		git clone https://github.com/voicekit-team/T-one.git; \
	fi
	@if ! command -v poetry > /dev/null 2>&1; then \
		echo "Poetry is not installed. Installing Poetry..."; \
		curl -sSL https://install.python-poetry.org | python3 -; \
	fi
	@echo "Installing dependencies with Poetry..."
	@echo "Note: This may take several minutes, especially when building kenlm..."
	@echo "If you encounter network timeouts, simply retry: make install"
	@CMAKE=$(which cmake) poetry install --no-interaction || ( \
		echo ""; \
		echo "=========================================="; \
		echo "Installation failed!"; \
		echo "=========================================="; \
		echo ""; \
		echo "If you see 'TimeoutError' or 'Read timed out':"; \
		echo "  This is a network issue. Simply retry:"; \
		echo "    make install"; \
		echo ""; \
		echo "If kenlm installation fails repeatedly:"; \
		echo "  1. Install kenlm separately:"; \
		echo "     poetry run pip install kenlm"; \
		echo "  2. Then retry:"; \
		echo "     poetry install"; \
		echo ""; \
		echo "Other common issues:"; \
		echo "  - Missing cmake: sudo apt-get install cmake build-essential"; \
		echo "  - Missing build tools: sudo apt-get install build-essential"; \
		echo ""; \
		exit 1; \
	)
	@echo "Installation complete!"
	@echo ""
	@echo "To use Redis storage, run: make install-redis"

# Install with Redis support
install-redis:
	@echo "Installing T-one REST API with Redis support..."
	@if ! command -v cmake > /dev/null 2>&1; then \
		echo "ERROR: cmake is required but not found."; \
		echo "Please install cmake first:"; \
		echo "  Ubuntu/Debian: sudo apt-get install cmake"; \
		echo "  macOS: brew install cmake"; \
		echo "  Or download from: https://cmake.org/download/"; \
		exit 1; \
	fi
	@if [ ! -d "T-one" ]; then \
		echo "Cloning T-One repository..."; \
		git clone https://github.com/voicekit-team/T-one.git; \
	fi
	@if ! command -v poetry > /dev/null 2>&1; then \
		echo "Poetry is not installed. Installing Poetry..."; \
		curl -sSL https://install.python-poetry.org | python3 -; \
	fi
	@echo "Installing dependencies with Redis support..."
	@echo "Note: This may take several minutes, especially when building kenlm..."
	@echo "If you encounter network timeouts, simply retry: make install-redis"
	@CMAKE=$(which cmake) poetry install --extras redis --no-interaction || ( \
		echo ""; \
		echo "=========================================="; \
		echo "Installation failed!"; \
		echo "=========================================="; \
		echo ""; \
		echo "If you see 'TimeoutError' or 'Read timed out':"; \
		echo "  This is a network issue. Simply retry:"; \
		echo "    make install-redis"; \
		echo ""; \
		echo "If kenlm installation fails repeatedly:"; \
		echo "  1. Install kenlm separately:"; \
		echo "     poetry run pip install kenlm"; \
		echo "  2. Then retry:"; \
		echo "     poetry install --extras redis"; \
		echo ""; \
		echo "Other common issues:"; \
		echo "  - Missing cmake: sudo apt-get install cmake build-essential"; \
		echo "  - Missing build tools: sudo apt-get install build-essential"; \
		echo ""; \
		exit 1; \
	)
	@echo "Installation complete with Redis support!"
	@echo ""
	@echo "To use Redis storage, set environment variables:"
	@echo "  export STORAGE_TYPE=redis"
	@echo "  export REDIS_URL=redis://localhost:6379/0"
	@echo ""
	@echo "Make sure Redis is running before starting the API server."

# Run the API server
run:
	@echo "Starting ASR API server..."
	poetry run uvicorn asr_api.main:app --host 0.0.0.0 --port 8000 --reload

# Clean up
clean:
	@echo "Cleaning up..."
	@if [ -d "T-one" ]; then \
		echo "Removing T-One directory..."; \
		rm -rf T-one; \
	fi
	@if [ -d ".venv" ]; then \
		echo "Removing virtual environment..."; \
		rm -rf .venv; \
	fi
	@if [ -d "__pycache__" ]; then \
		echo "Removing Python cache..."; \
		find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true; \
		find . -type f -name "*.pyc" -delete 2>/dev/null || true; \
	fi
	@echo "Cleanup complete!"

# Docker commands
docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting services with docker-compose..."
	@echo "Available services:"
	@echo "  - api: Memory storage (port 8000)"
	@echo "  - api-redis: Redis storage (port 8001)"
	@echo "  - redis: Redis server (port 6379)"
	@echo ""
	@echo "Usage examples:"
	@echo "  docker-compose up -d api          # Start API with memory storage"
	@echo "  docker-compose up -d api-redis redis  # Start API with Redis"
	docker-compose up -d

docker-down:
	@echo "Stopping docker-compose services..."
	docker-compose down

docker-logs:
	@echo "Viewing docker-compose logs..."
	docker-compose logs -f

