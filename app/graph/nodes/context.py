from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graph.state import ArchivistState
from app.mcp_clients.github import get_pr_diff
from app.utils.config import LLM_MODEL

class IntentExtraction(BaseModel):
    domains: list[str] = Field(
        description="List of architectural domains touched by this code (e.g., 'Database', 'Frontend', 'Auth', 'CI/CD')"
    )

async def extract_context(state: ArchivistState) -> dict:
    print("\n--- CONTEXT AGENT: Fetching and filtering diff ---")
    
    repo = state["repo_full_name"]
    pr_num = state["pr_number"]
    
    raw_diff = state.get("pr_diff", "")
    if not raw_diff:
        try:
            raw_diff = await get_pr_diff(repo, pr_num)
        except Exception as e:
            print(f"Failed to fetch diff from GitHub: {e}")
            return {"extracted_intents": []}
        
    print("\n--- CONTEXT AGENT: Extracting Architectural Intents ---")
    
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0)
    structured_llm = llm.with_structured_output(IntentExtraction)
    
    prompt = f"""
    Review this code diff and identify the core architectural domains being modified.
    Return a list of domains.
    
    Code Diff:
    {raw_diff[:25000]} 
    """
    
    result = structured_llm.invoke(prompt)
    print(f"Identified Domains: {result.domains}")
    
    return {
        "pr_diff": raw_diff,
        "extracted_intents": result.domains
    }