# See here for image contents: https://github.com/devcontainers/templates/tree/main/src/ubuntu

ARG VARIANT=3.13-trixie
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

RUN \
    apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y bash-completion \
    && echo 'source /usr/share/bash-completion/bash_completion' >> /root/.bashrc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
