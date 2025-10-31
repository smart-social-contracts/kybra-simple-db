FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Install additional system dependencies for Python development
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        build-essential \
        git \
        curl \
        wget \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*
