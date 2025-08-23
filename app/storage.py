"""
S3 storage utilities for MP3 + RSS feed.
"""

import os
import boto3
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

s3 = boto3.client("s3", region_name=AWS_REGION)

def upload_file(local_path: Path, key: str) -> str:
    """
    Upload a file to S3 and return its public URL.
    """
    # Guess content type based on extension
    if local_path.suffix == ".mp3":
        content_type = "audio/mpeg"
    elif local_path.suffix in [".xml", ".rss"]:
        content_type = "application/rss+xml"
    else:
        content_type = "binary/octet-stream"

    s3.upload_file(
        Filename=str(local_path),
        Bucket=AWS_BUCKET_NAME,
        Key=key,
        ExtraArgs={"ContentType": content_type}
    )

    return f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
