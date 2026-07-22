from botocore.exceptions import ClientError
from app.core.config import settings
from fastapi import HTTPException
import boto3
import uuid
import os


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
    region_name=settings.AWS_REGION
)


def upload_file(file, company_id: int, project_id: int):

    file_extension = os.path.splitext(file.filename)[1]
    original_name = os.path.splitext(file.filename)[0]

    unique_filename = (
        f"{uuid.uuid4().hex}_{original_name}{file_extension}"
    )

    file_key = (
        f"company-{company_id}/"
        f"project-{project_id}/"
        f"{unique_filename}"
    )

    try:

        s3_client.upload_fileobj(
            Fileobj=file.file,
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=file_key,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )

        return file_key

    except ClientError:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload file to S3"
        )


def delete_file(file_key: str):

    try:

        s3_client.delete_object(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=file_key
        )

    except ClientError:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete file from S3"
        )


def get_file_url(file_key: str):

    try:

        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": settings.AWS_S3_BUCKET_NAME,
                "Key": file_key
            },
            ExpiresIn=3600
        )

        return url

    except ClientError:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate file URL"
        )