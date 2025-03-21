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

# Expose ports for HTTP and SSE transports
EXPOSE 8000

# Set default transport to stdio
ENV KALTURA_MCP_TRANSPORT=stdio

# Run server with configurable transport
CMD ["sh", "-c", "kaltura-mcp"]