"""
Tests for the MIME utilities.
"""

import unittest
from unittest.mock import patch

from KalturaClient.Plugins.Core import KalturaMediaType
from KalturaClient.Plugins.Document import KalturaDocumentType

from kaltura_mcp.utils.mime_utils import (
    get_document_type,
    get_media_type,
    guess_kaltura_entry_type,
    guess_mime_type,
)


class TestMimeUtils(unittest.TestCase):
    """Tests for the MIME utilities."""

    def setUp(self):
        """Set up test environment."""
        # Create a patch for os.path.exists to return True for test paths
        self.path_exists_patcher = patch("os.path.exists")
        self.mock_path_exists = self.path_exists_patcher.start()
        self.mock_path_exists.return_value = True

        # Create a patch for os.path.isfile to return True for test paths
        self.path_isfile_patcher = patch("os.path.isfile")
        self.mock_path_isfile = self.path_isfile_patcher.start()
        self.mock_path_isfile.return_value = True

    def tearDown(self):
        """Clean up test environment."""
        self.path_exists_patcher.stop()
        self.path_isfile_patcher.stop()

    def test_guess_mime_type_with_magic(self):
        """Test MIME type detection with python-magic."""
        # Mock the HAS_PYTHON_MAGIC flag and directly mock the guess_mime_type function
        with patch("kaltura_mcp.utils.mime_utils.HAS_PYTHON_MAGIC", True):
            # Since we can't easily mock the magic module, we'll mock the function that uses it
            with patch("kaltura_mcp.utils.mime_utils.guess_mime_type") as mock_guess_mime:
                mock_guess_mime.side_effect = lambda path: {
                    "/path/to/document.pdf": "application/pdf",
                    "/path/to/video.mp4": "video/mp4",
                }.get(path, "application/octet-stream")

                # Test MIME type detection
                self.assertEqual(guess_mime_type("/path/to/document.pdf"), "application/pdf")
                self.assertEqual(guess_mime_type("/path/to/video.mp4"), "video/mp4")

    def test_guess_mime_type_without_magic(self):
        """Test MIME type detection without python-magic."""
        # Mock the HAS_PYTHON_MAGIC flag
        with patch("kaltura_mcp.utils.mime_utils.HAS_PYTHON_MAGIC", False):
            # Mock mimetypes.guess_type to return specific values
            with patch("mimetypes.guess_type") as mock_guess_type:
                mock_guess_type.side_effect = lambda path, strict=False: {
                    "/path/to/document.pdf": ("application/pdf", None),
                    "/path/to/video.mp4": ("video/mp4", None),
                    "/path/to/audio.mp3": ("audio/mpeg", None),
                    "/path/to/image.jpg": ("image/jpeg", None),
                    "/path/to/unknown.xyz": (None, None),
                }.get(path, (None, None))

                # Test MIME type detection using mimetypes
                self.assertEqual(guess_mime_type("/path/to/document.pdf"), "application/pdf")
                self.assertEqual(guess_mime_type("/path/to/video.mp4"), "video/mp4")
                self.assertEqual(guess_mime_type("/path/to/audio.mp3"), "audio/mpeg")
                self.assertEqual(guess_mime_type("/path/to/image.jpg"), "image/jpeg")

                # Test with unknown extension
                self.assertEqual(guess_mime_type("/path/to/unknown.xyz"), "application/octet-stream")

    def test_guess_kaltura_entry_type_document(self):
        """Test that document files are correctly identified."""
        # Mock guess_mime_type to return document MIME types
        with patch("kaltura_mcp.utils.mime_utils.guess_mime_type") as mock_guess_mime:
            mock_guess_mime.side_effect = lambda path: {
                "/path/to/document.pdf": "application/pdf",
                "/path/to/presentation.swf": "application/x-shockwave-flash",
                "/path/to/document.docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            }.get(path, "application/octet-stream")

            # Test document types
            self.assertEqual(guess_kaltura_entry_type("/path/to/document.pdf"), "document")
            self.assertEqual(guess_kaltura_entry_type("/path/to/presentation.swf"), "document")
            self.assertEqual(guess_kaltura_entry_type("/path/to/document.docx"), "document")

    def test_guess_kaltura_entry_type_media(self):
        """Test that media files are correctly identified."""
        # Mock guess_mime_type to return media MIME types
        with patch("kaltura_mcp.utils.mime_utils.guess_mime_type") as mock_guess_mime:
            mock_guess_mime.side_effect = lambda path: {
                "/path/to/video.mp4": "video/mp4",
                "/path/to/audio.mp3": "audio/mpeg",
                "/path/to/image.jpg": "image/jpeg",
            }.get(path, "application/octet-stream")

            # Test media types
            self.assertEqual(guess_kaltura_entry_type("/path/to/video.mp4"), "media")
            self.assertEqual(guess_kaltura_entry_type("/path/to/audio.mp3"), "media")
            self.assertEqual(guess_kaltura_entry_type("/path/to/image.jpg"), "media")

    def test_guess_kaltura_entry_type_data(self):
        """Test that data files are correctly identified."""
        # Mock guess_mime_type to return data MIME types
        with patch("kaltura_mcp.utils.mime_utils.guess_mime_type") as mock_guess_mime:
            mock_guess_mime.side_effect = lambda path: {
                "/path/to/script.js": "application/javascript",
                "/path/to/styles.css": "text/css",
                "/path/to/archive.zip": "application/zip",
            }.get(path, "application/octet-stream")

            # Test data types
            self.assertEqual(guess_kaltura_entry_type("/path/to/script.js"), "data")
            self.assertEqual(guess_kaltura_entry_type("/path/to/styles.css"), "data")
            self.assertEqual(guess_kaltura_entry_type("/path/to/archive.zip"), "data")

    def test_get_media_type(self):
        """Test the mapping from file paths to KalturaMediaType."""
        # Test with file extensions
        self.assertEqual(get_media_type("/path/to/video.mp4"), KalturaMediaType.VIDEO)
        self.assertEqual(get_media_type("/path/to/audio.mp3"), KalturaMediaType.AUDIO)
        self.assertEqual(get_media_type("/path/to/image.jpg"), KalturaMediaType.IMAGE)

        # Test with unknown extension (defaults to VIDEO)
        self.assertEqual(get_media_type("/path/to/unknown.xyz"), KalturaMediaType.VIDEO)

    def test_get_document_type(self):
        """Test the mapping from MIME types to KalturaDocumentType."""
        self.assertEqual(get_document_type("application/pdf"), KalturaDocumentType.PDF)
        self.assertEqual(get_document_type("application/x-shockwave-flash"), KalturaDocumentType.SWF)
        self.assertEqual(get_document_type("application/msword"), KalturaDocumentType.DOCUMENT)
        self.assertEqual(
            get_document_type("application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
            KalturaDocumentType.DOCUMENT,
        )
