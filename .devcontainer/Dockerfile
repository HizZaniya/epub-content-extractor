FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git ca-certificates gnupg jq shellcheck \
    libjpeg-dev libpng-dev libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI (gh)
RUN install -d -m 0755 /etc/apt/keyrings \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
       -o /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
       > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash vscode
USER vscode

# mise (Python + Node.js version management)
ENV PATH="/home/vscode/.local/share/mise/shims:/home/vscode/.local/bin:$PATH"
RUN curl https://mise.run | sh && mise use --global python@3.13 node@22

# uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/home/vscode/.local/bin sh

# bash-language-server (consumed by the claude-code-lsps bash plugin)
RUN npm install -g bash-language-server pyright

# Claude Code (native install, stable channel)
RUN curl -fsSL https://claude.ai/install.sh | bash -s stable
