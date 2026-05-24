import os
from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graph.state import ArchivistState
from app.utils.filters import filter_junk_files
from app.mcp_clients.github import get_pr_diff

class IntentOutput(BaseModel):
    domains: List[str] = Field(
        description="List of core architectural domains modified in this PR (e.g., 'Database', 'Frontend', 'Authentication')."
    )

async def extract_context(state: ArchivistState) -> dict:
    print("\n--- CONTEXT AGENT: Fetching and filtering diff ---")
    repo = state["repo_full_name"]
    pr_num = state["pr_number"]
    
    raw_diff = await get_pr_diff(repo, pr_num)
    clean_diff = filter_junk_files(raw_diff)
    
    print("--- CONTEXT AGENT: Extracting Architectural Intents ---")
    
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(IntentOutput)
    
    prompt = f"""
    You are an expert Staff Engineer reviewing a Pull Request. 
    Analyze the following code diff and identify the high-level architectural domains being modified.
    Return ONLY the domain categories, not specific file names or variables.
    
    Code Diff:
    {clean_diff[:25000]}  # Truncating to ensure we don't blow up context for massive PRs
    """
    
    result = structured_llm.invoke(prompt)
    intents = result.domains if result else []
    
    print(f"Identified Domains: {intents}")
    
    # Return the dictionary to update the LangGraph state
    return {"pr_diff": clean_diff, "extracted_intents": intents}