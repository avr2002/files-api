"""Error cases for the OpenAI API routes."""

from fastapi import status
from fastapi.testclient import TestClient

from files_api.schemas import GeneratedFileType

TEST_FILE_PATH = "some/nested/path/file.txt"


def test_generated_file_already_exists(client: TestClient):
    """Test generating file that already exists."""
    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": TEST_FILE_PATH,
            "prompt": "Test Prompt",
            "file_type": GeneratedFileType.TEXT.value,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": TEST_FILE_PATH,
            "prompt": "Test Prompt",
            "file_type": GeneratedFileType.TEXT.value,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "file_path": TEST_FILE_PATH,
        "message": "File already exists. Please use a different file name.",
    }


def test_alternate_file_type(client: TestClient):
    """Test using wrong file type."""
    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": TEST_FILE_PATH,
            "prompt": "Test Prompt",
            "file_type": GeneratedFileType.AUDIO.value,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_wrong_file_format(client: TestClient):
    """Test wrong file format."""
    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": "some/nested/path/image.pdf",
            "prompt": "Test Prompt",
            "file_type": GeneratedFileType.IMAGE.value,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_unknown_file_type(client: TestClient):
    """Test using unknown file type."""
    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": TEST_FILE_PATH,
            "prompt": "Test Prompt",
            "file_type": "UnknownFileType",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_empty_fields_in_request_body(client: TestClient):
    """Test missing fields in the request body."""
    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": TEST_FILE_PATH,
            "prompt": "Test Prompt",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_empty_prompt(client: TestClient):
    """Test empty prompt."""
    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": TEST_FILE_PATH,
            "prompt": "",
            "file_type": GeneratedFileType.TEXT.value,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_case_insensitive_file_type(client: TestClient):
    """Test case-insensitive file type."""
    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": TEST_FILE_PATH,
            "prompt": "Test Prompt",
            "file_type": "text",  # Lowercase
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
