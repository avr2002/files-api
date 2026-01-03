FROM python:3.12-slim-bookworm

WORKDIR /app

# copy/create bare minimum files needed to install dependencies
COPY pyproject.toml README.md uv.lock /app/
RUN mkdir -p /app/src/files_api/
RUN touch /app/src/files_api/__init__.py

# Set environment variables for uv to use the system Python environment
ENV UV_SYSTEM_PYTHON=true
ENV VIRTUAL_ENV=/usr/local/
ENV PATH="/usr/local/bin:$PATH"

# install dependencies from pyproject.toml
RUN pip install --upgrade pip uv
RUN uv sync --no-cache --group=docker --frozen --active --project=/app/
# RUN source /app/.venv/bin/activate
# RUN uv pip install --no-cache --group=docker --editable "/app/"
# RUN pip install --editable "/app/[docker]"


# copy the rest of the source code
COPY ./src/ /app/src/

# create the s3 bucket if desired(if false then using real S3 bucket), then start the fastapi app
CMD (\
    if [ "$CREATE_BUCKET_ON_STARTUP" = "true" ]; then \
        uv run --active -- python -c "import boto3; boto3.client('s3').create_bucket(Bucket='${S3_BUCKET_NAME}')"; \
    fi \
    ) \
    && uv run --active -- uvicorn files_api.main:create_app --factory --host 0.0.0.0 --port 8000 --reload