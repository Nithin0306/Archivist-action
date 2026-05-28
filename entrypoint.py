import os
import json
import asyncio

import httpx
from app.graph.workflow import archivist_app
from app.mcp_clients.github import get_pr_files

async def run_action():
    print("🚀 Booting up Archivist GitHub Action...")
    
    event_path = os.getenv("GITHUB_EVENT_PATH")
    with open(event_path, "r") as f:
        payload = json.load(f)
        
    pr = payload.get("pull_request")
    if not pr:
        print("Not a pull request event. Exiting.")
        return

    repo_full_name = payload.get("repository", {}).get("full_name")
    pr_number = pr.get("number")
    
    pr_file_paths = await get_pr_files(repo_full_name, pr_number)
    
    initial_state = {
        "repo_full_name": repo_full_name,
        "pr_number": pr_number,
        "pr_title": pr.get("title", ""),
        "pr_body": pr.get("body") or "",
        "pr_head_sha": pr.get("head", {}).get("sha"),
        "pr_file_paths": pr_file_paths
    }
    
    await archivist_app.ainvoke(initial_state)
    print("Archivist Action completed successfully.")

async def handle_dismiss_override(repo: str, pr_number: int):
    # Bypasses the AI and forces the commit status to green
    print(f"🚨 Override command detected for PR #{pr_number}! Forcing green status...")
    
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with httpx.AsyncClient() as client:
        # Fetches the PR details to get the latest commit SHA
        pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
        pr_resp = await client.get(pr_url, headers=headers)
        pr_resp.raise_for_status()
        head_sha = pr_resp.json()["head"]["sha"]

        # Overwrites the commit status to "success"
        status_url = f"https://api.github.com/repos/{repo}/statuses/{head_sha}"
        payload = {
            "state": "success",
            "description": "Violation dismissed by developer override.",
            "context": "Archivist Architecture Review" 
        }
        status_resp = await client.post(status_url, headers=headers, json=payload)
        status_resp.raise_for_status()
        print("✅ Status successfully overridden to green. PR is unlocked!")


async def main():
    event_name = os.getenv("GITHUB_EVENT_NAME")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    if event_name == "issue_comment":
        with open(event_path, 'r') as f:
            event = json.load(f)
        
        # Verify this comment is on a Pull Request (GitHub treats PRs as Issues)
        if "pull_request" in event.get("issue", {}):
            comment_body = event.get("comment", {}).get("body", "").strip()
            
            if comment_body.lower() == "/archivist_dismiss":
                repo = os.getenv("GITHUB_REPOSITORY")
                pr_number = event["issue"]["number"]
                await handle_dismiss_override(repo, pr_number)
                return
                
        print("Comment ignored. Not an override command.")
        return

    elif event_name == "pull_request":
        print("🚀 Pull Request event detected. Booting up LangGraph...")
        await run_action()

if __name__ == "__main__":
    asyncio.run(main())