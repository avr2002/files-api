"""Fixtures for FastAPI test client."""

import pytest
from fastapi.testclient import TestClient

from files_api.main import create_app
from files_api.settings import Settings
from tests.consts import TEST_BUCKET_NAME


# Fixture for FastAPI test client
@pytest.fixture
def client(mocked_aws, mocked_openai) -> TestClient:
    """Pytest fixture to provide a FastAPI test client."""
    settings: Settings = Settings(s3_bucket_name=TEST_BUCKET_NAME)
    app = create_app(settings=settings)
    with TestClient(app) as client:
        yield client
