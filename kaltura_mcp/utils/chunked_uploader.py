"""
Chunked file uploader for Kaltura MCP Server.

This module provides a robust implementation for uploading files to Kaltura
using chunked uploading with adaptive chunk sizing. It handles large files
efficiently by breaking them into manageable chunks and implements retry
logic for network errors.
"""

import asyncio
import logging
import os
import time
from typing import Any, Optional

import aiohttp
import anyio
from KalturaClient.Plugins.Core import (
    KalturaUploadToken,
    KalturaUploadTokenStatus,
)

logger = logging.getLogger(__name__)


class TokenNotFinalizedError(Exception):
    """
    Raised when the Kaltura upload token fails to reach FULL_UPLOAD within the allowed attempts.

    This can happen if there are issues with the Kaltura API or if the upload was interrupted.
    """

    pass


class ChunkedUploader:
    """
    Handles file uploads to Kaltura via chunked uploading with optional adaptive chunk size.

    This class provides a robust implementation for uploading files to Kaltura using
    chunked uploading. It supports adaptive chunk sizing based on upload speed and
    implements retry logic for network errors.

    Args:
        kaltura_client: KalturaClientWrapper instance
        chunk_size_kb: Initial chunk size in KB (default ~2MB)
        adaptive_chunking: If True, dynamically adjust chunk size based on measured speed
        target_upload_time: Target seconds per chunk to guide chunk resizing
        min_chunk_size_kb: Minimum chunk size in KB (adaptive)
        max_chunk_size_kb: Maximum chunk size in KB (adaptive)
        verbose: Enable debug-level logging if True

    Raises:
        ValueError: If chunk_size_kb is less than 1
    """

    def __init__(
        self,
        kaltura_client: Any,
        chunk_size_kb: int = 2048,
        adaptive_chunking: bool = False,
        target_upload_time: float = 5.0,
        min_chunk_size_kb: int = 1024,
        max_chunk_size_kb: int = 102400,
        verbose: bool = False,
    ) -> None:
        if chunk_size_kb < 1:
            raise ValueError("chunk_size_kb must be at least 1 KB")

        self.kaltura_client = kaltura_client
        self.verbose = verbose
        self.adaptive_chunking = adaptive_chunking
        self.target_upload_time = target_upload_time
        self.min_chunk_size_kb = min_chunk_size_kb
        self.max_chunk_size_kb = max_chunk_size_kb

        self.chunk_size_kb = float(chunk_size_kb)
        self.chunk_size_bytes = int(self.chunk_size_kb * 1024)

        if self.verbose:
            logger.debug(
                "Initialized ChunkedUploader with chunk_size=%.2f KB, adaptive_chunking=%s, "
                "target_upload_time=%.1f s, min_chunk_size_kb=%d, max_chunk_size_kb=%d",
                self.chunk_size_kb,
                self.adaptive_chunking,
                self.target_upload_time,
                self.min_chunk_size_kb,
                self.max_chunk_size_kb,
            )

    def _adjust_chunk_size(self, upload_time: float, current_chunk_size_bytes: int) -> None:
        """
        Adjust chunk size based on measured upload time, aiming for target_upload_time.

        This method dynamically adjusts the chunk size based on the measured upload speed
        to achieve the target upload time per chunk. It respects the minimum and maximum
        chunk size constraints.

        Args:
            upload_time: Time taken to upload the current chunk in seconds
            current_chunk_size_bytes: Size of the current chunk in bytes
        """
        if not self.adaptive_chunking or upload_time <= 0:
            return

        current_chunk_kb = current_chunk_size_bytes / 1024.0
        current_speed_kb_s = current_chunk_kb / upload_time
        ideal_chunk_size_kb = current_speed_kb_s * self.target_upload_time

        old_chunk_size_kb = self.chunk_size_kb
        # Use a weighted average to avoid drastic changes
        new_chunk_size_kb = (old_chunk_size_kb + ideal_chunk_size_kb) / 2.0
        # Ensure the chunk size stays within the defined bounds
        bounded_chunk_size_kb = max(self.min_chunk_size_kb, min(self.max_chunk_size_kb, new_chunk_size_kb))

        self.chunk_size_kb = bounded_chunk_size_kb
        self.chunk_size_bytes = int(bounded_chunk_size_kb * 1024)

        if self.verbose:
            logger.debug(
                "Adaptive chunking: old=%.2fKB, new=%.2fKB, speed=%.2fKB/s, time=%.2fs",
                old_chunk_size_kb,
                self.chunk_size_kb,
                current_speed_kb_s,
                upload_time,
            )

    async def upload_file(self, file_path: str) -> str:
        """
        Upload the file in chunks to Kaltura and return the KalturaUploadToken ID.

        This method handles the complete file upload process:
        1. Validates the file
        2. Creates an upload token
        3. Uploads the file in chunks
        4. Finalizes the upload

        Args:
            file_path: Path to the file to upload

        Returns:
            Upload token ID

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the path is not a valid file or the file is empty
            aiohttp.ClientError: If there's a network error during upload
            TokenNotFinalizedError: If the upload token cannot be finalized
        """
        # Validate file
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' does not exist.")
        if not os.path.isfile(file_path):
            raise ValueError(f"Path '{file_path}' is not a valid file.")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError(f"File '{file_path}' is empty. Aborting upload.")

        if self.verbose:
            logger.debug(f"File size of '{file_path}' is {file_size} bytes.")

        try:
            # 1) Create upload token
            upload_token = await self._create_upload_token(file_path, file_size)
            offset = 0

            # 2) Chunked upload
            async with aiohttp.ClientSession() as session:
                with open(file_path, "rb") as infile:
                    while offset < file_size:
                        chunk = infile.read(self.chunk_size_bytes)
                        if not chunk:  # Reached EOF earlier than expected
                            break
                        is_final_chunk = (offset + len(chunk)) >= file_size

                        start_time = time.time()
                        await self._upload_chunk(
                            session,
                            upload_token.id,
                            chunk,
                            offset,
                            resume=(offset > 0),
                            is_final_chunk=is_final_chunk,
                        )
                        elapsed = time.time() - start_time

                        offset += len(chunk)
                        if self.verbose:
                            logger.debug(
                                f"Uploaded {len(chunk)} bytes in {elapsed:.2f}s "
                                f"(offset {offset}/{file_size}, final: {is_final_chunk})"
                            )

                        self._adjust_chunk_size(elapsed, len(chunk))

            # 3) Finalize the upload
            await self._finalize_upload_token(upload_token.id, file_size)
            logger.info(f"Successfully uploaded file '{file_path}' with token ID {upload_token.id}")
            return upload_token.id  # type: ignore

        except aiohttp.ClientError as e:
            logger.error(f"Network error during upload of '{file_path}': {e}")
            raise
        except Exception as e:
            logger.error(f"Error uploading file '{file_path}': {e}")
            raise

    async def _create_upload_token(self, file_path: str, file_size: int) -> KalturaUploadToken:
        """
        Create a Kaltura upload token for the file to be uploaded.

        Args:
            file_path: Path to the file
            file_size: Size of the file in bytes

        Returns:
            KalturaUploadToken object

        Raises:
            Exception: If the Kaltura API call fails
        """
        token = KalturaUploadToken()
        token.fileName = os.path.basename(file_path)
        token.fileSize = file_size

        if self.verbose:
            logger.debug(f"Creating upload token for '{token.fileName}' ({file_size} bytes).")

        try:
            return await self.kaltura_client.execute_request("uploadToken", "add", uploadToken=token)
        except Exception as e:
            logger.error(f"Failed to create upload token for '{token.fileName}': {e}")
            raise

    async def _upload_chunk(
        self,
        session: aiohttp.ClientSession,
        upload_token_id: str,
        chunk: bytes,
        offset: int,
        resume: bool,
        is_final_chunk: bool,
    ) -> None:
        """
        Upload a single chunk with retry logic for network errors.

        Args:
            session: aiohttp ClientSession for HTTP requests
            upload_token_id: ID of the upload token
            chunk: Bytes to upload
            offset: Byte offset in the file
            resume: Whether this is a resumed upload
            is_final_chunk: Whether this is the final chunk

        Raises:
            aiohttp.ClientError: If the upload fails after all retries
        """
        max_attempts = 5
        delay = 1.0  # seconds

        for attempt in range(1, max_attempts + 1):
            try:
                # Prepare form data
                form_data = aiohttp.FormData()
                form_data.add_field("resume", "1" if resume else "0")
                form_data.add_field("resumeAt", str(offset))
                form_data.add_field("finalChunk", "1" if is_final_chunk else "0")
                form_data.add_field(
                    "fileData",
                    chunk,
                    filename=f"chunk_{offset}",
                    content_type="application/octet-stream",
                )

                # Get upload URL and parameters
                upload_url = f"{self.kaltura_client.get_service_url()}/api_v3/service/uploadtoken/action/upload"
                params = {
                    "uploadTokenId": upload_token_id,
                    "ks": self.kaltura_client.get_ks(),
                }

                # Upload the chunk
                async with session.post(upload_url, data=form_data, params=params, timeout=30) as response:
                    response.raise_for_status()
                    return

            except (aiohttp.ClientError, TimeoutError, asyncio.TimeoutError) as e:
                if attempt == max_attempts:
                    logger.error(f"Attempt {attempt}/{max_attempts} failed with error: {e}. No more retries.")
                    raise
                logger.warning(f"Attempt {attempt}/{max_attempts} failed with error: {e}. " f"Retrying in {delay:.1f}s...")
                await anyio.sleep(delay)
                delay *= 2.0  # Exponential backoff

    async def _finalize_upload_token(self, upload_token_id: str, file_size: int) -> None:
        """
        Poll until the token is FULL_UPLOAD or fail after several attempts.

        This method checks the status of the upload token and waits until it reaches
        the FULL_UPLOAD status, indicating that the upload is complete and the file
        is ready to be used.

        Args:
            upload_token_id: ID of the upload token
            file_size: Size of the file in bytes

        Raises:
            TokenNotFinalizedError: If the token doesn't reach FULL_UPLOAD status
        """
        max_attempts = 5
        delay = 1.0  # seconds

        for attempt in range(1, max_attempts + 1):
            try:
                token = await self.kaltura_client.execute_request("uploadToken", "get", uploadTokenId=upload_token_id)

                if await self._validate_upload_token_status(token, file_size):
                    # If it's FULL_UPLOAD, we're done
                    return

                # Otherwise, if we haven't reached max attempts, sleep and retry
                if attempt < max_attempts:
                    if self.verbose:
                        logger.debug(
                            f"Upload token {upload_token_id} is not FULL_UPLOAD on attempt "
                            f"{attempt}/{max_attempts}; waiting {delay:.1f}s before next check..."
                        )
                    await anyio.sleep(delay)
                    delay *= 2.0  # Exponential backoff
            except Exception as e:
                logger.error(f"Error checking upload token status: {e}")
                if attempt < max_attempts:
                    await anyio.sleep(delay)
                    delay *= 2.0
                else:
                    raise

        # If we exhaust all attempts, raise an error
        raise TokenNotFinalizedError(f"Upload token {upload_token_id} not finalized after {max_attempts} attempts.")

    async def _validate_upload_token_status(self, upload_token: Any, file_size: int) -> bool:
        """
        Check if the upload token status is FULL_UPLOAD (completed).

        Args:
            upload_token: KalturaUploadToken object
            file_size: Expected file size in bytes

        Returns:
            True if the token status is FULL_UPLOAD, False otherwise
        """
        status_value = upload_token.status.getValue() if hasattr(upload_token.status, "getValue") else upload_token.status
        if status_value == KalturaUploadTokenStatus.FULL_UPLOAD:
            logger.info(
                f"Upload token {upload_token.id} finalized: {upload_token.fileName} - "
                f"{upload_token.uploadedFileSize}/{file_size} bytes"
            )
            return True

        if self.verbose:
            logger.debug(f"Current upload token status for {upload_token.id}: {status_value} (not FULL_UPLOAD).")
        return False
