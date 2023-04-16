ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-alpine

RUN apk add --no-cache \
        curl \
        gcc \
        libressl-dev \
        musl-dev \
        libffi-dev && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile=minimal && \
    source $HOME/.cargo/env && \
    pip install --no-cache-dir poetry==1.4.1 && \
    apk del \
        curl \
        gcc \
        libressl-dev \
        musl-dev \
        libffi-dev && \
    mkdir -p /bot/bot

# Install project dependencies
WORKDIR /bot
COPY ./bot ./bot
COPY poetry.lock pyproject.toml LICENSE README.md ./
RUN poetry config virtualenvs.create false && \
    poetry install


ENTRYPOINT ["poetry"]
CMD ["run", "python", "-m", "bot"]
