import os
import json
import asyncio
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

if __name__ == "__main__":
    asyncio.run(run_action())