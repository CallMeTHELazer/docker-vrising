import os
import sys
import tarfile
import datetime
import boto3
from pathlib import Path

# Load configuration from environment variables (passed by GitHub Actions)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "pokeru-games")

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    print("Error: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables must be set.")
    sys.exit(1)

# Get prefix (legacy or current)
prefix = sys.argv[1] if len(sys.argv) > 1 else "current"
if prefix not in ["legacy", "current"]:
    print("Error: Prefix must be 'legacy' or 'current'")
    sys.exit(1)

# Save directory on the host machine
SAVE_DIR = Path("/home/steam/Vrising-Dedicated-Server/data/Saves/v4/Pokeru1")
if not SAVE_DIR.exists():
    print(f"Error: Save directory {SAVE_DIR} does not exist.")
    sys.exit(1)

# Create backup temp archive
timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
archive_name = f"vrising-backup-{timestamp}.tar.gz"
temp_archive_path = Path(f"/tmp/{archive_name}")

print(f"Creating local compressed archive: {temp_archive_path}...")
try:
    with tarfile.open(temp_archive_path, "w:gz") as tar:
        tar.add(SAVE_DIR, arcname=SAVE_DIR.name)
except Exception as e:
    print("Error creating archive:", e)
    sys.exit(1)

print("Connecting to Amazon S3...")
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# S3 Object Key (Path in S3)
s3_key = f"vrising/{prefix}/{archive_name}"

print(f"Uploading to S3 bucket '{AWS_S3_BUCKET}' as '{s3_key}'...")
try:
    s3_client.upload_file(str(temp_archive_path), AWS_S3_BUCKET, s3_key)
    print("S3 Upload completed successfully!")
except Exception as e:
    print("Error uploading to S3:", e)
    sys.exit(1)
finally:
    # Cleanup temp local archive
    if temp_archive_path.exists():
        temp_archive_path.unlink()
        print("Temp local archive cleaned up.")
