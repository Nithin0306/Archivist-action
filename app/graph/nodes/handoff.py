from app.graph.state import ArchivistState
from app.mcp_clients.github import post_pr_comment, set_commit_status

async def handoff_to_github(state: ArchivistState) -> dict:
    print("\n--- HANDOFF AGENT: Drafting Comment ---")
    
    repo = state["repo_full_name"]
    pr_num = state["pr_number"]
    sha = state.get("pr_head_sha", "")
    reasoning = state["evaluation_result"]
    
    comment_body = f"""## 🏛️ Archivist: Architectural Governance Alert
🚨 **Architectural Drift Detected**
{reasoning}
---
*Reply with `/archivist dismiss` to override this block and accept the technical debt.*"""
    
    # Skips GitHub API if running via local CLI
    if pr_num == 0:
        print("Local CLI run detected. Skipping GitHub comment and status update.")
        return {"final_comment": comment_body}
    
    # Otherwise, post to GitHub
    try:
        await post_pr_comment(repo, pr_num, comment_body)
        if sha:
            await set_commit_status(repo, sha, "failure", "Architectural violation detected.")
    except Exception as e:
        print(f"Failed to post to GitHub: {e}")
    
    return {"final_comment": comment_body}