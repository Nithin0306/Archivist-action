import os
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

github_mcp = FastMCP("Archivist-GitHub")

def get_github_token() -> str:
    # Retrieves the built-in GitHub token provided by the GitHub Action environment.

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable is missing!")
    return token

@github_mcp.tool()
async def get_pr_diff(repo_full_name: str, pr_number: int) -> str:
    # Fetches the raw code diff for a specific Pull Request
    token = get_github_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff" # requests raw diff format
    }
    
    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.text

@github_mcp.tool()
async def post_pr_comment(repo_full_name: str, pr_number: int, body: str) -> str:
    # Posts a comment to a GitHub pull request
    token = get_github_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
        response = await client.post(url, headers=headers, json={"body": body})
        response.raise_for_status()
        return f"Comment posted successfully to PR #{pr_number}"
    

@github_mcp.tool()
async def get_pr_files(repo_full_name: str, pr_number: int) -> list[str]:
    # Fetches the list of file paths modified in a specific Pull Request

    token = get_github_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        
        files_data = response.json()
        file_paths = [file["filename"] for file in files_data]
        
        return file_paths
    
    
@github_mcp.tool()
async def set_commit_status(repo_full_name: str, sha: str, state: str, description: str) -> str:
    """
    Sets the commit status. 'state' must be one of: error, failure, pending, success.
    """

    token = get_github_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    payload = {
        "state": state,
        "description": description[:140], 
        "context": "Archivist / Architectural Review" 
    }
    
    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com/repos/{repo_full_name}/statuses/{sha}"
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return f"Status '{state}' set for commit {sha[:7]}"

@github_mcp.tool()
async def get_pr_head_sha(repo_full_name: str, pr_number: int) -> str:
    """Fetches the HEAD commit SHA for a given PR."""

    token = get_github_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}"
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["head"]["sha"]