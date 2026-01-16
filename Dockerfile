FROM python:3.12-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# copy/create bare minimum files needed to install dependencies
COPY pyproject.toml README.md uv.lock /app/
RUN mkdir -p /app/src/files_api/
RUN touch /app/src/files_api/__init__.py

ENV UV_SYSTEM_PYTHON=false

# install dependencies
RUN uv sync --frozen --no-cache --group=docker --project=/app/ --compile-bytecode

# # Set environment variables for uv to use the system Python environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
# ENV PATH="/app/.venv/bin:$PATH"


# copy the rest of the source code
COPY ./src/ /app/src/
COPY ./tests/mocks /app/tests/mocks

# create the s3 bucket if desired(if false then using real S3 bucket), then start the fastapi app
CMD (\
    if [ "$CREATE_BUCKET_ON_STARTUP" = "true" ]; then \
        uv run --active -- python -c "import boto3; boto3.client('s3').create_bucket(Bucket='${S3_BUCKET_NAME}')"; \
    fi \
    ) \
    && uv run --active -- uvicorn files_api.main:create_app --factory --host 0.0.0.0 --port 8000 --reload

# """
# Refer these three documentation:
# - https://docs.astral.sh/uv/guides/integration/docker/#getting-started
# - https://docs.astral.sh/uv/guides/integration/fastapi/#migrating-an-existing-fastapi-project
# - https://docs.astral.sh/uv/guides/integration/aws-lambda/#using-uv-with-aws-lambda
# - https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path
# """