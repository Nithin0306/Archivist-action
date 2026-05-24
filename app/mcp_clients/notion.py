import os
from mcp.server.fastmcp import FastMCP

knowledge_mcp = FastMCP("Archivist-Knowledge")

@knowledge_mcp.tool()
def search_adrs(keywords: list[str]) -> str:

    # Just returns the contents of the local dummy ADR for testing purpose
    try:
        with open("ADR/ADR-001.md", "r") as f:
            content = f.read()
            return f"Found 1 relevant ADR:\n\n{content}"
    except FileNotFoundError:
        return "No ADRs found."