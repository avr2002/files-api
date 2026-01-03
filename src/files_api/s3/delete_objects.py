"""Functions for deleting objects from an S3 bucket--the "D" in CRUD."""

from typing import Optional

import boto3

from files_api.s3.read_objects import object_exists_in_s3

try:
    from mypy_boto3_s3 import S3Client
except ImportError:
    ...


def delete_s3_object(bucket_name: str, object_key: str, s3_client: Optional["S3Client"] = None) -> None:
    """
    Delete an object from the S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :param object_key: Key of the object to delete.
    :param s3_client: Optional S3 client to use. If not provided, a new client will be created.
    """
    s3_client = s3_client or boto3.client("s3")
    if object_exists_in_s3(bucket_name=bucket_name, object_key=object_key, s3_client=s3_client):
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
