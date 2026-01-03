"""Happy path tests for the OpenAI routes."""

from fastapi import status
from fastapi.testclient import TestClient

from files_api.schemas import GeneratedFileType

TEST_FILE_PATH = "some/nested/path/file.txt"


def test_generate_text(client: TestClient):
    """Test generating text using POST method."""
    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": TEST_FILE_PATH,
            "prompt": "Test Prompt",
            "file_type": GeneratedFileType.TEXT.value,
        },
    )

    respone_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert (
        respone_data["message"]
        == f"New {GeneratedFileType.TEXT.value} file generated and uploaded at path: {TEST_FILE_PATH}"
    )

    # Get the generated file
    response = client.get(f"/v1/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b"This is a mock response from the chat completion endpoint."
    assert response.headers["Content-Type"] == "text/plain"


def test_generate_image(client: TestClient):
    """Test generating image using POST method."""
    IMAGE_FILE_PATH = "some/nested/path/image.png"  # pylint: disable=invalid-name  # noqa: N806
    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": IMAGE_FILE_PATH,
            "prompt": "Test Prompt",
            "file_type": GeneratedFileType.IMAGE.value,
        },
    )

    respone_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert (
        respone_data["message"]
        == f"New {GeneratedFileType.IMAGE.value} file generated and uploaded at path: {IMAGE_FILE_PATH}"
    )

    # Get the generated file
    response = client.get(f"/v1/files/{IMAGE_FILE_PATH}")
    assert response.status_code == status.HTTP_200_OK
    assert response.content is not None
    assert response.headers["Content-Type"] == "image/png"


def test_generate_audio(client: TestClient):
    """Test generating an audio file using the POST method."""
    audio_file_path = "some-audio.mp3"
    response = client.post(
        url="/v1/files/generated",
        json={
            "file_path": audio_file_path,
            "prompt": "Test Prompt",
            "file_type": GeneratedFileType.AUDIO.value,
        },
    )

    response_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    # message=f"New {query_params.file_type.value} file generated and uploaded at path: {query_params.file_path}",
    assert response_data["message"] == (
        f"New {GeneratedFileType.AUDIO.value} file generated and uploaded at path: {audio_file_path}"
    )

    # Get the generated file
    response = client.get(f"/v1/files/{audio_file_path}")
    assert response.status_code == status.HTTP_200_OK
    assert response.content is not None
    assert response.headers["Content-Type"] == "audio/mpeg"
