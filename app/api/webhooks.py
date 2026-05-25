import logging
from fastapi import APIRouter, Request, BackgroundTasks
from app.graph.workflow import archivist_app
from app.mcp_clients.github import get_pr_files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("archivist")

router = APIRouter()

async def run_archivist_pipeline(initial_state: dict):
    # Runs the LangGraph pipeline in the background
    logger.info(f"Triggering AI pipeline for PR #{initial_state['pr_number']}")
    try:
        # ainvoke runs the graph asynchronously
        await archivist_app.ainvoke(initial_state)
        logger.info(f"Pipeline completed for PR #{initial_state['pr_number']}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

@router.post("/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    
    if "pull_request" not in payload:
        return {"status": "ignored", "reason": "Not a pull request event"}
        
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    pr_number = pr.get("number")
    repo_full_name = payload.get("repository", {}).get("full_name")
    
    if pr.get("draft") is True:
        logger.info(f"Dropped PR #{pr_number}: Draft status.")
        return {"status": "ignored", "reason": "Draft PR"}
        
    if pr.get("state") == "closed":
        logger.info(f"Dropped PR #{pr_number}: Closed status.")
        return {"status": "ignored", "reason": "Closed PR"}
        
    valid_actions = {"opened", "reopened", "synchronize", "ready_for_review"}
    if action not in valid_actions:
        return {"status": "ignored", "reason": f"Action '{action}' ignored"}

    logger.info(f"Accepted PR #{pr_number} ({action}): {pr.get('title')}")
    
    pr_title = pr.get("title", "")
    pr_body = pr.get("body") or ""              # GitHub sometimes sends None for an empty description, so default it to ""

    
    try:
        pr_file_paths = await get_pr_files(repo_full_name, pr_number)
    except Exception as e:
        logger.error(f"Failed to fetch files for PR #{pr_number}: {e}")
        pr_file_paths = []

    initial_state = {
        "repo_full_name": repo_full_name,
        "pr_number": pr_number,
        "pr_title": pr_title,
        "pr_body": pr_body,
        "pr_file_paths": pr_file_paths
    }
    
    background_tasks.add_task(run_archivist_pipeline, initial_state)
    
    # Instantly return 200 OK to GitHub to prevent timeouts
    return {"status": "accepted", "message": "Archivist pipeline triggered in background."}