# Use the official uv image with Python 3.12 and Debian as the base
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy only the dependency files first for better caching
COPY shellserver/pyproject.toml shellserver/uv.lock ./shellserver/

# Install dependencies (creates .venv in /app/shellserver)
RUN cd shellserver && uv sync --venv

# Copy the rest of your app code
COPY shellserver/ ./shellserver/
# If your app depends on files outside shellserver, copy them as well
# COPY path/to/other/files /app/path/to/other/files

# Set the working directory to where server.py is
WORKDIR /app/shellserver

# Expose any ports if needed (optional, MCP stdio transport does not require this)
# EXPOSE 8000

# Run the MCP server using uv in the virtual environment
CMD ["uv", "run", "server.py"]