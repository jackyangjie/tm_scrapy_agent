"""File upload and serving API endpoints.

This module provides API endpoints for:
- File upload from base64-encoded data
- Serving uploaded files by file_id
"""

import base64
import logging
import mimetypes
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from util.file_util import save_file_from_base64, UPLOADS_DIR


class UploadRequest(BaseModel):
    """Request model for file upload.

    Attributes:
        filename: Original filename of the uploaded file
        file_data: Base64-encoded file data or data URL
    """

    filename: str = Field(default="uploaded_file", description="Original filename")
    file_data: str = Field(..., description="Base64-encoded file data or data URL")


async def upload_file_handler(body: UploadRequest) -> dict:
    """Handle file upload from base64-encoded data.

    Args:
        body: Request body containing filename and file_data (base64 or data URL)

    Returns:
        dict with file_id, file_url, filename, size on success
        dict with error and status code on failure

    Examples:
        >>> request = UploadRequest(filename="test.txt", file_data="SGVsbG8=")
        >>> result = await upload_file_handler(request)
        >>> print(result['file_id'])
        'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    """
    try:
        if not body.file_data:
            return {"error": "Missing file_data", "status": 400}

        # Use save_file_from_base64 function from util
        result = save_file_from_base64(body.file_data, body.filename)

        logging.info(
            f"文件上传成功 - FileID: {result['file_id']}, "
            f"Filename: {result['filename']}, Size: {result['size']} bytes"
        )

        return result
    except ValueError as e:
        logging.error(f"文件上传失败: {e}")
        return {"error": str(e), "status": 400}
    except Exception as e:
        logging.error(f"文件上传失败（未知错误）: {e}", exc_info=True)
        return {"error": "Internal server error", "status": 500}


async def serve_file_handler(file_id: str) -> dict:
    """Serve uploaded files by file_id.

    Args:
        file_id: UUID of the uploaded file

    Returns:
        dict with file_id, filename, content_type, size, content (base64-encoded)
        dict with error and status code if file not found

    Examples:
        >>> result = await serve_file_handler("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
        >>> print(result['filename'])
        'example.pdf'
    """
    file_dir = os.path.join(UPLOADS_DIR, file_id)

    # Check if directory exists
    if not os.path.exists(file_dir):
        return {"error": "File not found", "status": 404}

    # Find the file in the directory (there's only one file per directory)
    files = list(Path(file_dir).glob("*"))
    if not files or not files[0].is_file():
        return {"error": "File not found", "status": 404}

    file_path = files[0]

    # Determine content type
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = "application/octet-stream"

    # Read and return file content
    try:
        with open(file_path, "rb") as f:
            content = f.read()

        # Return file info and content
        return {
            "file_id": file_id,
            "filename": file_path.name,
            "content_type": content_type,
            "size": len(content),
            "content": base64.b64encode(content).decode("utf-8"),
        }
    except Exception as e:
        logging.error(f"Error serving file {file_id}: {e}")
        return {"error": str(e), "status": 500}
