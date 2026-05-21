import logging
from fastapi import APIRouter, Request

# basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("archivist")

router = APIRouter()

@router.post("/github")
async def github_webhook(request: Request):
    # GitHub sends the payload as JSON
    payload = await request.json()

    if "pull_request" not in payload:
        return {"status": "ignored", "reason": "Not a pull request event"}
    
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    pr_number = pr.get("number")

    # drafts
    if pr.get("draft") is True:
        logger.info(f"Dropped PR #{pr_number}: Draft status.")
        return {"status": "ignored", "reason": "Draft PR"}
    
    # closed PRs
    if pr.get("state") == "closed":
        logger.info(f"Dropped PR #{pr_number}: Closed status.")
        return {"status": "ignored", "reason": "Closed PR"}
    
    # act only on specific state changes
    valid_actions = {"opened", "reopened", "synchronize", "ready_for_review"}
    if action not in valid_actions:
        logger.info(f"Dropped PR #{pr_number}: Action '{action}' is not actionable.")
        return {"status": "ignored", "reason": f"Action '{action}' ignored"}
    
    logger.info(f"=> Accepted PR #{pr_number} ({action}): {pr.get('title')}")

    print("\nINCOMING PR PAYLOAD")
    print(f"Repository: {payload.get('repository', {}).get('full_name')}")
    print(f"Diff URL: {pr.get('diff_url')}")

    return {"status": "accepted"}