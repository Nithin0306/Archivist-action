import asyncio
from app.graph.state import ArchivistState
from app.mcp_clients.github import post_pr_comment

async def handoff_to_github(state: ArchivistState) -> dict:
    print("\n--- HANDOFF AGENT: Drafting and posting GitHub Comment ---")
    
    repo = state["repo_full_name"]
    pr_num = state["pr_number"]
    reasoning = state["evaluation_result"]
    
    comment_body = f"""## Archivist: Architectural Governance Alert

🚨 **Architectural Drift Detected**

I reviewed this Pull Request against our internal Architecture Decision Records (ADRs) and found a violation.

### Details:
{reasoning}

---
*Reply with `/archivist dismiss` to override this block and accept the technical debt.*
"""
    
    # MCP tool posts the comment
    await post_pr_comment(repo, pr_num, comment_body)
    print(f"Comment successfully posted to PR #{pr_num}!")
    
    return {"final_comment": comment_body}