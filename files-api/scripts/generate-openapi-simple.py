# pylint: disable=invalid-name
"""
Simple script that generates an OpenAPI schema for the FastAPI application.

If there is an existing OpenAPI schema on disk, this script will compare the
generated schema to the existing schema. If they are different AT ALL, the script will
exit with an error code.

The idea is that this logic can be run in CI. If the developer forgot to
regenerate the OpenAPI schema after making code changes to FastAPI that would
change the schema, then the build will fail.

This ensures that the
OpenAPI schema committed to the repo will always be a reflection of what
the neighboring FastAPI code would generate. In other words, this script
allows us to assume that the openapi.json file in the repo is always
up to date.

We take advantage of this assumption using the `oasdiff` CLI tool.
When a PR is opened to main. We simply need to use `oasdiff` to compare
the commit `feature-branch:/openapi.json` against `main:/openapi.json`.

This script is not as feature-rich as `generate-openapi.py` but is useful to get
a sense of how to generate an OpenAPI schema for a FastAPI application. This is
the core of how the more advanced `generate-openapi.py` script works.
"""

import json
import sys
from pathlib import Path

from fastapi.openapi.utils import get_openapi

from files_api.main import create_app
from files_api.settings import Settings

OUTPUT_SPEC = Path("openapi.json")


def main() -> None:
    generated_openapi_schema = generate_openapi()
    schemas_are_equal = schemas_match(generated_schema=generated_openapi_schema)
    write_openapi_to_disk(openapi_schema=generated_openapi_schema)
    print("✅ Wrote OpenAPI schema to disk.")
    if not schemas_are_equal:
        print("❌ Existing OpenAPI schema does not match generated schema.")
        sys.exit(1)


# pylint: disable=duplicate-code
def generate_openapi() -> dict:
    """
    Generate the OpenAPI schema for the FastAPI application.

    Official docs for generating the FastAPI schema:
    https://fastapi.tiangolo.com/how-to/extending-openapi/?h=get_open#generate-the-openapi-schema
    """
    settings = Settings(s3_bucket_name="placeholder")
    app = create_app(settings=settings)
    return get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        summary=app.summary,
        description=app.description,
        tags=app.openapi_tags,
        servers=app.servers,
        license_info=app.license_info,
        contact=app.contact,
        terms_of_service=app.terms_of_service,
        routes=app.routes,
    )


def write_openapi_to_disk(openapi_schema: dict) -> None:
    OUTPUT_SPEC.write_text(json.dumps(openapi_schema, indent=2), encoding="utf-8")


def schemas_match(generated_schema: dict) -> bool:
    if not OUTPUT_SPEC.exists():
        return False
    existing_schema = json.loads(OUTPUT_SPEC.read_text(encoding="utf-8"))
    return existing_schema == generated_schema


if __name__ == "__main__":
    main()
