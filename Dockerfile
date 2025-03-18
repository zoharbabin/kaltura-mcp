FROM python:3.10-slim

WORKDIR /app

# Copy source code first
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8000

# Run server
CMD ["kaltura-mcp"]