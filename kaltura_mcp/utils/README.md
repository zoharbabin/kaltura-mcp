# Kaltura MCP Utilities

This directory contains utility modules for the Kaltura MCP Server that enhance its functionality, particularly for file uploads and MIME type detection.

## Modules

### mime_utils.py

Provides utilities for MIME type detection and mapping to Kaltura entry types:

- `guess_mime_type(file_path)`: Determines the MIME type of a file using python-magic if available, otherwise falls back to extension-based detection.
- `guess_kaltura_entry_type(file_path)`: Maps a file to the appropriate Kaltura entry type ("media", "document", or "data").
- `get_media_type(file_path)`: Maps a file to the appropriate KalturaMediaType enum value.
- `get_document_type(mime_type)`: Maps a MIME type to the appropriate KalturaDocumentType enum value.

### chunked_uploader.py

Implements a robust chunked file upload mechanism for Kaltura:

- `ChunkedUploader`: A class that handles file uploads to Kaltura via chunked uploading with optional adaptive chunk sizing.
  - Supports large file uploads by breaking them into manageable chunks
  - Features adaptive chunk sizing based on upload speed
  - Implements retry logic for network errors
  - Validates upload token status to ensure successful uploads

## Usage

These utilities are primarily used by the `EnhancedMediaUploadToolHandler` in `tools/enhanced_media.py`, which provides a more robust file upload experience compared to the basic `MediaUploadToolHandler`.

### Example

```python
from kaltura_mcp.utils.mime_utils import guess_kaltura_entry_type, guess_mime_type
from kaltura_mcp.utils.chunked_uploader import ChunkedUploader

# Determine file type
file_path = "/path/to/file.pdf"
entry_type = guess_kaltura_entry_type(file_path)  # Returns "document"
mime_type = guess_mime_type(file_path)  # Returns "application/pdf"

# Upload file
uploader = ChunkedUploader(kaltura_client, chunk_size_kb=2048, adaptive_chunking=True)
upload_token_id = await uploader.upload_file(file_path)
```

## Dependencies

- `python-magic`: For accurate MIME type detection (optional but recommended)
- `aiohttp`: For asynchronous HTTP requests
- `requests-toolbelt`: For multipart form data handling