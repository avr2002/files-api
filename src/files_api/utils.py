import json
import os
import urllib.request


# Use the AWS-Parameters-and-Secrets-Lambda-Extension to retrieve secrets from Secrets Manager
# ref: https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html
def get_secret_from_extension(secret_name: str) -> str:
    """Retrieves a secret value from the Secrets Manager extension."""
    # The extension runs on localhost port 2773 by default
    _extension_routing_port: str = os.environ["PARAMETERS_SECRETS_EXTENSION_HTTP_PORT"]

    # AWS_SESSION_TOKEN is required for authentication with the extension with the Secrets Manager
    _aws_session_auth_token: str = os.environ["AWS_SESSION_TOKEN"]

    endpoint = f"http://localhost:{_extension_routing_port}/secretsmanager/get?secretId={secret_name}"

    # Use the session token to authenticate with the extension
    req = urllib.request.Request(url=endpoint)
    req.add_header("X-Aws-Parameters-Secrets-Token", _aws_session_auth_token)

    # Request/Respone Syntax: https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    with urllib.request.urlopen(req) as response:
        secret_response = response.read().decode("utf-8")
        # The response is a JSON string containing the secret value
        secret_data = json.loads(secret_response)
        return secret_data["SecretString"]


# ref: https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html
def get_parameter_from_extension(name: str, decrypt: bool = True) -> str:
    """Retrieve an SSM parameter via the local extension with optional decryption."""
    extension_port: str = os.getenv("AWS_LAMBDA_RUNTIME_API_PORT", "2773")
    aws_session_auth_token: str = os.environ["AWS_SESSION_TOKEN"]

    endpoint = f"http://localhost:{extension_port}/systemsmanager/parameters/get?name={name}"
    if decrypt:
        endpoint += "&withDecryption=true"

    req = urllib.request.Request(url=endpoint)
    req.add_header("X-Aws-Parameters-Secrets-Token", aws_session_auth_token)

    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))
        # Response shape mirrors SSM GetParameter API
        return data["Parameter"]["Value"]
