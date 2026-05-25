import os
import time
import jwt
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

github_mcp = FastMCP("Archivist-GitHub")

def get_github_token() -> str:
    # Generates a short-lived installation access token for the GitHub app
    app_id = os.getenv("GITHUB_APP_ID")
    key_path = os.getenv("GITHUB_PRIVATE_KEY_PATH")
    
    with open(key_path, 'r') as f:
        private_key = f.read()

    # Creates the JWT (valid for 10 minutes)
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": app_id
    }
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

    # Get the Installation ID (Assumes app is installed on 1 repo for now)
    headers = {
        "Authorization": f"Bearer {encoded_jwt}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    with httpx.Client() as client:
        # Fetch installations for this app
        resp = client.get("https://api.github.com/app/installations", headers=headers)
        resp.raise_for_status()
        install_id = resp.json()[0]["id"]
        
        # Exchange JWT for installation access token
        token_resp = client.post(
            f"https://api.github.com/app/installations/{install_id}/access_tokens",
            headers=headers
        )
        token_resp.raise_for_status()
        return token_resp.json()["token"]

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