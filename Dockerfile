ARG PYTHON_VERSION=3.11
ARG POETRY_VERSION=1.4.1

FROM python:${PYTHON_VERSION}-alpine

RUN apk add --no-cache \
        curl \
        gcc \
        libressl-dev \
        musl-dev \
        libffi-dev && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile=minimal && \
    source $HOME/.cargo/env && \
    pip install --no-cache-dir poetry==${POETRY_VERSION} && \
    apk del \
        curl \
        gcc \
        libressl-dev \
        musl-dev \
        libffi-dev

# Install project dependencies
WORKDIR /bot
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install --without dev

# Copy the source code in last to optimize rebuilding the image
COPY . .

ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
