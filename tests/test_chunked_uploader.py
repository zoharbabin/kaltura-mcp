"""
Tests for the ChunkedUploader class.
"""

from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest
from KalturaClient.Plugins.Core import KalturaUploadTokenStatus

from kaltura_mcp.utils.chunked_uploader import ChunkedUploader, TokenNotFinalizedError


class TestChunkedUploader:
    """Tests for the ChunkedUploader class."""

    @pytest.fixture
    def mock_kaltura_client(self):
        """Create a mock Kaltura client."""
        client = MagicMock()
        client.execute_request = AsyncMock()
        client.get_service_url = MagicMock(return_value="https://www.kaltura.com/")
        client.get_ks = MagicMock(return_value="fake-ks")
        return client

    @pytest.fixture
    def uploader(self, mock_kaltura_client):
        """Create a ChunkedUploader instance with a mock client."""
        return ChunkedUploader(mock_kaltura_client, chunk_size_kb=1024, adaptive_chunking=True, verbose=True)

    def test_init(self, mock_kaltura_client):
        """Test the initialization of ChunkedUploader."""
        uploader = ChunkedUploader(
            mock_kaltura_client,
            chunk_size_kb=2048,
            adaptive_chunking=True,
            target_upload_time=3.0,
            min_chunk_size_kb=512,
            max_chunk_size_kb=8192,
            verbose=True,
        )

        assert uploader.chunk_size_kb == 2048
        assert uploader.chunk_size_bytes == 2048 * 1024
        assert uploader.adaptive_chunking is True
        assert uploader.target_upload_time == 3.0
        assert uploader.min_chunk_size_kb == 512
        assert uploader.max_chunk_size_kb == 8192
        assert uploader.verbose is True
        assert uploader.kaltura_client == mock_kaltura_client

    def test_init_invalid_chunk_size(self, mock_kaltura_client):
        """Test initialization with invalid chunk size."""
        with pytest.raises(ValueError, match="chunk_size_kb must be at least 1 KB"):
            ChunkedUploader(mock_kaltura_client, chunk_size_kb=0)

    @pytest.mark.anyio
    async def test_create_upload_token(self, uploader, mock_kaltura_client):
        """Test the _create_upload_token method."""
        # Mock the response from the Kaltura API
        mock_token = MagicMock()
        mock_token.id = "test_token_id"
        mock_kaltura_client.execute_request.return_value = mock_token

        # Call the method
        result = await uploader._create_upload_token("/path/to/file.mp4", 1024)

        # Verify the result
        assert result == mock_token
        mock_kaltura_client.execute_request.assert_called_once()
        args, kwargs = mock_kaltura_client.execute_request.call_args
        assert args[0] == "uploadToken"
        assert args[1] == "add"
        assert kwargs["uploadToken"].fileName == "file.mp4"
        assert kwargs["uploadToken"].fileSize == 1024

    @pytest.mark.anyio
    async def test_upload_file_success(self, uploader, mock_kaltura_client):
        """Test the upload_file method with a successful upload."""
        # Mock file operations
        with (
            patch("os.path.exists", return_value=True),
            patch("os.path.isfile", return_value=True),
            patch("os.path.getsize", return_value=4096),
            patch("builtins.open", mock_open(read_data=b"test" * 1024)),
            patch("aiohttp.ClientSession") as mock_session_class,
            patch.object(uploader, "_create_upload_token") as mock_create_token,
            patch.object(uploader, "_upload_chunk") as mock_upload_chunk,
            patch.object(uploader, "_finalize_upload_token") as mock_finalize,
        ):

            # Mock the token creation
            mock_token = MagicMock()
            mock_token.id = "test_token_id"
            mock_create_token.return_value = mock_token

            # Mock the ClientSession
            mock_session = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            # Call the method
            token_id = await uploader.upload_file("/path/to/file.mp4")

            # Verify the result
            assert token_id == "test_token_id"
            mock_create_token.assert_called_once_with("/path/to/file.mp4", 4096)
            assert mock_upload_chunk.call_count > 0
            mock_finalize.assert_called_once_with("test_token_id", 4096)

    @pytest.mark.anyio
    async def test_upload_file_nonexistent(self, uploader):
        """Test upload_file with a nonexistent file."""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                await uploader.upload_file("/path/to/nonexistent.mp4")

    @pytest.mark.anyio
    async def test_upload_file_not_a_file(self, uploader):
        """Test upload_file with a path that is not a file."""
        with (
            patch("os.path.exists", return_value=True),
            patch("os.path.isfile", return_value=False),
        ):
            with pytest.raises(ValueError):
                await uploader.upload_file("/path/to/directory")

    @pytest.mark.anyio
    async def test_upload_file_empty(self, uploader):
        """Test upload_file with an empty file."""
        with (
            patch("os.path.exists", return_value=True),
            patch("os.path.isfile", return_value=True),
            patch("os.path.getsize", return_value=0),
        ):
            with pytest.raises(ValueError):
                await uploader.upload_file("/path/to/empty.mp4")

    @pytest.mark.anyio
    async def test_adjust_chunk_size(self, uploader):
        """Test the _adjust_chunk_size method."""
        # Make sure initial chunk size is large enough to decrease
        uploader.chunk_size_kb = 2048.0
        uploader.chunk_size_bytes = int(uploader.chunk_size_kb * 1024)

        # Call the method with a fast upload (should increase chunk size)
        uploader._adjust_chunk_size(1.0, 1024 * 1024)  # 1MB in 1 second

        # Verify chunk size increased
        assert uploader.chunk_size_kb > 2048.0
        assert uploader.chunk_size_bytes > 2048 * 1024

        # Reset and test with a slow upload (should decrease chunk size)
        uploader.chunk_size_kb = 2048.0
        uploader.chunk_size_bytes = int(uploader.chunk_size_kb * 1024)

        uploader._adjust_chunk_size(10.0, 1024 * 1024)  # 1MB in 10 seconds

        # Verify chunk size decreased
        assert uploader.chunk_size_kb < 2048.0
        assert uploader.chunk_size_bytes < 2048 * 1024

    @pytest.mark.anyio
    async def test_validate_upload_token_status_success(self, uploader):
        """Test _validate_upload_token_status with a successful status."""
        # Create a mock token with FULL_UPLOAD status
        mock_token = MagicMock()
        mock_token.status = MagicMock(getValue=lambda: KalturaUploadTokenStatus.FULL_UPLOAD)
        mock_token.id = "test_token_id"
        mock_token.fileName = "test.mp4"
        mock_token.uploadedFileSize = 1024

        # Call the method
        result = await uploader._validate_upload_token_status(mock_token, 1024)

        # Verify the result
        assert result is True

    @pytest.mark.anyio
    async def test_validate_upload_token_status_not_ready(self, uploader):
        """Test _validate_upload_token_status with a not-ready status."""
        # Create a mock token with PENDING status
        mock_token = MagicMock()
        mock_token.status = MagicMock(getValue=lambda: KalturaUploadTokenStatus.PENDING)
        mock_token.id = "test_token_id"

        # Call the method
        result = await uploader._validate_upload_token_status(mock_token, 1024)

        # Verify the result
        assert result is False

    @pytest.mark.anyio
    async def test_finalize_upload_token_success(self, uploader, mock_kaltura_client):
        """Test _finalize_upload_token with a successful finalization."""
        # Mock the token get response
        mock_token = MagicMock()
        mock_token.status = MagicMock(getValue=lambda: KalturaUploadTokenStatus.FULL_UPLOAD)
        mock_token.id = "test_token_id"
        mock_token.fileName = "test.mp4"
        mock_token.uploadedFileSize = 1024
        mock_kaltura_client.execute_request.return_value = mock_token

        # Call the method
        await uploader._finalize_upload_token("test_token_id", 1024)

        # Verify the API call
        mock_kaltura_client.execute_request.assert_called_once_with("uploadToken", "get", uploadTokenId="test_token_id")

    @pytest.mark.anyio
    async def test_finalize_upload_token_failure(self, uploader, mock_kaltura_client):
        """Test _finalize_upload_token with a failed finalization."""
        # Mock the token get response with PENDING status
        mock_token = MagicMock()
        mock_token.status = MagicMock(getValue=lambda: KalturaUploadTokenStatus.PENDING)
        mock_token.id = "test_token_id"
        mock_kaltura_client.execute_request.return_value = mock_token

        # Call the method and expect an exception
        with patch("anyio.sleep") as mock_sleep:
            with pytest.raises(TokenNotFinalizedError):
                await uploader._finalize_upload_token("test_token_id", 1024)

            # Verify that sleep was called
            assert mock_sleep.call_count > 0
