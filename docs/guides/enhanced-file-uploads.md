# Enhanced File Upload Guide

This guide explains how to use the enhanced file upload capabilities in the Kaltura MCP Server.

## Overview

The Kaltura MCP Server now includes an enhanced file upload tool that provides the following features:

- **Chunked uploading** with adaptive chunk sizing for efficient handling of large files
- **Accurate file type detection** using MIME type analysis (with python-magic if available)
- **Support for all file types** including media (video, audio, image), documents (PDF, Office files), and data files
- **Robust error handling** with automatic retries for network issues
- **Category assignment** for uploaded files

## Using the Enhanced Upload Tool

### Tool Definition

The enhanced upload tool is available as `kaltura.media.upload` and accepts the following parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file_path | string | Yes | Path to the file to upload |
| name | string | Yes | Name of the entry |
| description | string | No | Description of the entry |
| tags | string | No | Comma-separated list of tags |
| access_control_id | integer | No | Access control ID to apply to the entry |
| conversion_profile_id | integer | No | Conversion profile ID to apply to the entry |
| category_id | integer | No | Category ID to assign the entry to |
| chunk_size_kb | integer | No | Initial chunk size in KB (default=2048) |
| adaptive_chunking | boolean | No | Enable adaptive chunking based on upload speed (default=true) |
| verbose | boolean | No | Enable verbose logging (default=false) |

### Example Usage

```python
# Example using the MCP client
from mcp.client import Client

async with Client() as client:
    result = await client.call_tool(
        "kaltura.media.upload",
        {
            "file_path": "/path/to/video.mp4",
            "name": "My Video",
            "description": "A sample video upload",
            "tags": "sample, video, upload",
            "category_id": 123,
            "chunk_size_kb": 4096,
            "adaptive_chunking": True
        }
    )
    print(result)
```

## File Type Support

The enhanced upload tool automatically detects the file type and creates the appropriate Kaltura entry:

### Media Files

- Video files (mp4, mov, avi, wmv, flv, mkv)
- Audio files (mp3, wav, aac, m4a, flac)
- Image files (jpg, jpeg, png, gif, bmp)

These are uploaded as `KalturaMediaEntry` with the appropriate media type.

### Document Files

- PDF files (pdf)
- Flash files (swf)
- Office documents (doc, docx, ppt, pptx, xls, xlsx)

These are uploaded as `KalturaDocumentEntry` with the appropriate document type.

### Data Files

- All other file types

These are uploaded as `KalturaDataEntry`.

## MIME Type Detection

The tool uses the following methods to detect MIME types:

1. If `python-magic` is installed, it uses libmagic to analyze the file content (most accurate)
2. Otherwise, it falls back to extension-based detection using Python's `mimetypes` module

## Chunked Uploading

Large files are uploaded in chunks to improve reliability and performance:

- Default chunk size is 2MB (2048 KB)
- With adaptive chunking enabled, the chunk size is adjusted based on upload speed
- Target upload time per chunk is 5 seconds by default
- Minimum chunk size is 1MB (1024 KB)
- Maximum chunk size is 100MB (102400 KB)

## Error Handling

The tool includes robust error handling:

- Network errors during chunk uploads are automatically retried with exponential backoff
- Upload token status is verified to ensure successful uploads
- Detailed error messages are provided in the response

## Response Format

The tool returns a JSON response with the following fields:

```json
{
  "id": "0_abc123",
  "name": "My Video",
  "description": "A sample video upload",
  "entryType": "media",
  "mimeType": "video/mp4",
  "uploadedFileSize": 1048576,
  "status": 2,
  "mediaType": 1,
  "duration": 60,
  "thumbnailUrl": "https://example.com/thumbnail.jpg",
  "createdAt": 1616161616,
  "message": "Media entry created successfully"
}
```

## Dependencies

To use all features of the enhanced upload tool, ensure the following dependencies are installed:

```
python-magic>=0.4.27
aiohttp>=3.8.5
requests-toolbelt>=1.0.0
```

These are included in the project dependencies but may require additional system libraries for `python-magic` to work correctly.