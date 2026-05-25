import os

async def get_mock_adrs(intents: list[str]) -> str:
    """
    Mock MCP tool that reads from a local Markdown file.
    Use this for local testing without hitting external APIs.
    """
    print("[MOCK] Fetching ADRs from local file...")
    try:
        with open("ADR/ADR-001.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No specific architectural rules found."