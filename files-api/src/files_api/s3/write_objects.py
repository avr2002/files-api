"""Functions for writing objects from an S3 bucket--the "C" and "U" in CRUD."""

from typing import Optional

import boto3
from aws_embedded_metrics.logger.metrics_logger import MetricsLogger

from files_api.monitoring.metrics import metrics_ctx

try:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_s3.type_defs import PutObjectOutputTypeDef
except ImportError:
    ...


# ContentType/MIME types helps browsers to render the content correctly.
# So when you download a file from S3 with specified ContentType, the browser will know how to render it.

# Common MIME types: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
# For example, "text/plain" for a text file, "image/jpeg" for a JPEG image, etc.

# boto3 does not allow ContentType to be passed as None and, so will be set to application/octet-stream by default.
# the ContentType="application/octet-stream", is a generic binary file.


def upload_s3_object(
    bucket_name: str,
    object_key: str,
    file_content: bytes,
    content_type: Optional[str] = None,
    s3_client: Optional["S3Client"] = None,
) -> "PutObjectOutputTypeDef":
    """Uploads a file to an S3 bucket.

    :param bucket_name: The name of the S3 bucket to upload the file to.
    :param object_key: path to the object in the bucket.
    :param file_content: The content of the file to upload.
    :param content_type: The MIME type of the file, e.g. "text/plain" for a text file.
    :param s3_client: An optional boto3 S3 client object. If not provided, one will be created.

    :returns: The response from the S3 API.
    """
    s3_client = s3_client or boto3.client("s3")
    # If content_type is None, set it to "application/octet-stream", the default MIME type used by S3.
    content_type = content_type or "application/octet-stream"
    response: "PutObjectOutputTypeDef" = s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=file_content,
        ContentType=content_type,
    )

    # not a terrific practice to have this generic upload function be aware of metrics
    # logging as well, e.g. what if we wanted to use this function outside the context of this app?
    # but for brevity we will include this here. A better approach would be to have a caller function
    # wrap this one, call it, and log the metric.
    metrics: MetricsLogger | None = metrics_ctx.get()
    if metrics:
        metrics.put_metric(key="S3BytesUploaded", value=len(file_content), unit="Bytes")

    return response
