# NetLicensing MCP Server
#
# Usage:
#   1. Build: docker build -t mcparmory-netlicensing .
#   2. Run:   docker run -p 8000:8000 --env-file .env mcparmory-netlicensing
#
# The .env file should contain your API credentials.
# See the generated .env file for required variables.
#
# Environment variables:
#   MCP_TRANSPORT - Transport mode: stdio, sse (default), streamable-http
#   MCP_HOST      - Host to bind to (default: 0.0.0.0)
#   MCP_PORT      - Port to listen on (default: 8000)

# =============================================================================
# Build stage
# =============================================================================
FROM python:3.11-slim as builder

WORKDIR /build

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Runtime stage
# =============================================================================
FROM python:3.11-slim

RUN groupadd --gid 1000 mcp && \
    useradd --uid 1000 --gid mcp --shell /bin/bash --create-home mcp

WORKDIR /app

LABEL org.opencontainers.image.title="NetLicensing MCP Server" \
      org.opencontainers.image.vendor="MCP Armory" \
      org.opencontainers.image.source="https://github.com/mcparmory/registry" \
      io.modelcontextprotocol.server.name="com.mcparmory/netlicensing"
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=mcp:mcp server.py .
COPY --chown=mcp:mcp _validators.py .
COPY --chown=mcp:mcp _model[s].py ./
COPY --chown=mcp:mcp _aut[h].py ./

USER mcp

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MCP_TRANSPORT=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/sse')" || exit 1

CMD ["sh", "-c", "python server.py --transport ${MCP_TRANSPORT} --host ${MCP_HOST} --port ${MCP_PORT}"]
