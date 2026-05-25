from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graph.state import ArchivistState
from app.mcp_clients.github import set_commit_status 

class EvaluationVerdict(BaseModel):
    violation_found: bool = Field(description="True if a violation occurred, False otherwise.")
    reasoning: str = Field(description="Detailed explanation of the verdict.")

async def evaluate_code(state: ArchivistState) -> dict:
    print("\n--- EVALUATION AGENT: Cross-referencing against ADRs ---")
    
    diff = state.get("pr_diff", "")
    title = state.get("pr_title", "")
    body = state.get("pr_body", "")
    files = state.get("pr_file_paths", [])
    adrs = state.get("relevant_adrs", "")
    
    repo = state.get("repo_full_name", "")
    sha = state.get("pr_head_sha", "")
    
    if "No specific architectural rules found" in adrs:
        print("No relevant ADRs to enforce. Passing PR.")
        
        if repo and sha:
            await set_commit_status(repo, sha, "success", "No applicable ADRs found. Code looks good.")
            
        return {"violation_found": False, "evaluation_result": "No applicable ADRs found."}

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
    structured_llm = llm.with_structured_output(EvaluationVerdict)
    
    if diff:
        context_block = f"--- PR Code Diff ---\n{diff[:25000]}"
        print("Evaluating based on FULL CODE DIFF.")
    else:
        context_block = f"--- PR Metadata ---\nTitle: {title}\nBody: {body}\nFiles: {files}"
        print("Evaluating based on METADATA (Fast Path).")
        
    prompt = f"""
    You are an expert Staff Engineer acting as an automated architectural governance engine.
    Review the following PR context against the provided Architecture Decision Records (ADRs).
    Determine IF the PR violates any of the strict rules laid out in the ADRs.
    
    --- ADRs (The Rules) ---
    {adrs}
    
    {context_block}
    """
    
    result = structured_llm.invoke(prompt)
    print(f"Verdict: {'🚨 VIOLATION' if result.violation_found else '✅ PASS'}")
    
    if not result.violation_found and repo and sha:
        await set_commit_status(repo, sha, "success", "Architectural review passed!")
    
    return {
        "violation_found": result.violation_found,
        "evaluation_result": result.reasoning
    }