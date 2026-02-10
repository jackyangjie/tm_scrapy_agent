"""File utility functions for file handling and validation.

This module provides utilities for:
- Filename sanitization to prevent path traversal attacks
- File size validation
- MIME type validation
- Saving files from base64 or binary data
- Processing file content in messages
"""

import base64
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Optional

from agentscope_runtime.engine.schemas.agent_schemas import FileContent
from agentscope.message import Msg

# Configure uploads directory
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "../uploads")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename

    Examples:
        >>> sanitize_filename("../../../etc/passwd")
        '______etc_passwd'
        >>> sanitize_filename("my document.pdf")
        'my_document.pdf'
        >>> sanitize_filename("")
        'unnamed_file'
    """
    if not filename:
        return "unnamed_file"

    # Remove leading/trailing whitespace
    filename = filename.strip()

    # Block path traversal patterns first (before any other processing)
    # Replace ".." with underscore anywhere in the filename
    filename = filename.replace("..", "_")

    # Preserve extension if filename starts with dot (e.g., ".pdf")
    if filename.startswith("."):
        ext = filename
        base_name = "file"
    else:
        # Split into base name and extension
        parts = filename.rsplit(".", 1)
        if len(parts) == 2:
            base_name, ext = parts[0], f".{parts[1]}"
        else:
            base_name, ext = filename, ""

    # Sanitize base name: replace special chars with underscore
    base_name = re.sub(r"[^\w\-]", "_", base_name)

    # Ensure base name is not empty after sanitization
    if not base_name or base_name.strip("_") == "":
        base_name = "file"

    return base_name + ext


def validate_file_size(file_data: bytes, max_size: int = 10 * 1024 * 1024) -> bool:
    """Check if file data size is within limit (default 10MB).

    Args:
        file_data: File binary data
        max_size: Maximum allowed size in bytes (default: 10MB)

    Returns:
        True if file size is within limit, False otherwise

    Examples:
        >>> validate_file_size(b"x" * 1000)
        True
        >>> validate_file_size(b"x" * (11 * 1024 * 1024))
        False
    """
    return len(file_data) <= max_size


def validate_mime_type(file_data: bytes) -> bool:
    """Validate MIME type using magic bytes.

    Since user requested "全部类型" (all types), this accepts all file types.
    For production, you could add more restrictive validation here.

    Args:
        file_data: File binary data

    Returns:
        Always True (accepting all types per user requirement)
    """
    # User requirement: accept all file types
    # If you need to restrict types, use mimetypes module here
    return True


def save_file_from_base64(file_data: str, filename: str) -> dict:
    """Save base64-encoded file to uploads directory.

    Args:
        file_data: Base64 string or data URL (data:mime/type;base64,...)
        filename: Original filename

    Returns:
        dict with keys: file_id, file_url, file_path, filename, size

    Raises:
        ValueError: If file size exceeds limit or base64 is invalid

    Examples:
        >>> result = save_file_from_base64("SGVsbG8gV29ybGQ=", "hello.txt")
        >>> print(result['file_id'])
        a1b2c3d4-e5f6-7890-abcd-ef1234567890
    """
    # Ensure uploads directory exists
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    # Detect and extract base64 from data URL if needed
    if file_data.startswith("data:"):
        # Extract base64 portion from data URL
        # Format: data:mime/type;base64,xxx
        if ";base64," in file_data:
            mime_type, b64_data = file_data.split(";base64,", 1)
        else:
            # Data URL without base64 encoding
            raise ValueError("Invalid data URL format")
    else:
        # Standard base64 string
        b64_data = file_data

    # Decode base64 to bytes
    try:
        file_bytes = base64.b64decode(b64_data)
    except (base64.binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid base64 data: {e}") from e

    # Validate file size (10MB limit)
    if not validate_file_size(file_bytes):
        raise ValueError(f"File size exceeds 10MB limit")

    # Generate UUID4 file_id
    file_id = str(uuid.uuid4())

    # Sanitize filename
    safe_filename = sanitize_filename(filename)

    # Create file_id subdirectory
    file_dir = os.path.join(UPLOADS_DIR, file_id)
    os.makedirs(file_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(file_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Generate file URL
    file_url = f"http://localhost:8080/files/{file_id}"

    return {
        "file_id": file_id,
        "file_url": file_url,
        "file_path": file_path,
        "filename": safe_filename,
        "size": len(file_bytes),
    }


def save_file_from_binary(file_data: bytes, filename: str) -> dict:
    """Save binary file to uploads directory.

    Args:
        file_data: File binary data
        filename: Original filename

    Returns:
        dict with keys: file_id, file_url, file_path, filename, size

    Raises:
        ValueError: If file size exceeds limit

    Examples:
        >>> result = save_file_from_binary(b"Hello World", "hello.txt")
        >>> print(result['file_id'])
        a1b2c3d4-e5f6-7890-abcd-ef1234567890
    """
    # Ensure uploads directory exists
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    # Validate file size (10MB limit)
    if not validate_file_size(file_data):
        raise ValueError(f"File size exceeds 10MB limit")

    # Generate UUID4 file_id
    file_id = str(uuid.uuid4())

    # Sanitize filename
    safe_filename = sanitize_filename(filename)

    # Create file_id subdirectory
    file_dir = os.path.join(UPLOADS_DIR, file_id)
    os.makedirs(file_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(file_dir, safe_filename)
    with open(file_path, "wb") as f:
        f.write(file_data)

    # Generate file URL
    file_url = f"http://localhost:8080/files/{file_id}"

    return {
        "file_id": file_id,
        "file_url": file_url,
        "file_path": file_path,
        "filename": safe_filename,
        "size": len(file_data),
    }


def process_file_content(item: FileContent, session_id: str) -> Optional[FileContent]:
    """Process a single FileContent item (save new uploads or validate existing).

    Args:
        item: FileContent to process
        session_id: Session identifier for logging

    Returns:
        Processed FileContent or None if processing failed
    """
    if item.file_data:
        try:
            filename = item.filename or "uploaded_file"
            result = save_file_from_base64(item.file_data, filename)
            item.file_id = result["file_id"]
            item.file_url = result["file_url"]
            logging.info(
                f"文件保存成功 - SessionID: {session_id}, "
                f"FileID: {result['file_id']}, "
                f"Filename: {result['filename']}, "
                f"Size: {result['size']} bytes"
            )
            return item
        except ValueError as e:
            logging.warning(f"文件处理失败 - SessionID: {session_id}, Error: {e}")
            return None
    elif item.file_url:
        logging.info(
            f"使用已有文件 - SessionID: {session_id}, FileURL: {item.file_url}"
        )
        return item
    else:
        logging.warning(
            f"文件内容无效 - SessionID: {session_id}, 缺少 file_data 和 file_url"
        )
        return None


def process_message_content(msg: Msg, session_id: str) -> None:
    """Process message content, handling files and text.

    Args:
        msg: Message to process
        session_id: Session identifier for logging
    """
    if not msg or not hasattr(msg, "content") or not msg.content:
        return

    processed_content = []
    for item in msg.content:
        if isinstance(item, FileContent):
            processed_item = process_file_content(item, session_id)
            if processed_item is not None:
                processed_content.append(processed_item)
        else:
            # TextContent or other types
            processed_content.append(item)

    msg.content = processed_content


def process_messages(msgs, session_id: str):
    """Process all messages, handling file uploads and content transformation.

    Args:
        msgs: Messages to process
        session_id: Session identifier for logging

    Returns:
        Processed messages
    """
    if msgs and hasattr(msgs, "__iter__"):
        processed_msgs = []
        for msg in msgs:
            process_message_content(msg, session_id)
            processed_msgs.append(msg)
        return processed_msgs
    return msgs
