FROM --platform=linux/amd64 python:3.11-bookworm

# prevent interactive prompts during installs
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive 

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && usermod -aG sudo $USERNAME # If you installed sudo

USER $USERNAME

WORKDIR /workspaces/calculator-agent-rl

# Keep the container running
CMD ["sleep", "infinity"]