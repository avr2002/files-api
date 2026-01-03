"""Utility functions for testing purposes."""

import boto3
import botocore


def delete_s3_bucket(bucket_name: str) -> None:
    """Delete an S3 bucket and all objects inside it."""
    try:
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchBucket":
            pass
        else:
            raise
