FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy source code first
COPY . .

# Run setup script in non-interactive mode
RUN python setup_kaltura_mcp.py --non-interactive --skip-venv --dev-deps

# Expose port
EXPOSE 8000

# Run server
CMD ["kaltura-mcp"]