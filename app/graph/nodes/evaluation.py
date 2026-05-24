from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graph.state import ArchivistState

class EvaluationVerdict(BaseModel):
    violation_found: bool = Field(description="True if the code diff violates the provided ADRs, False otherwise.")
    reasoning: str = Field(description="Detailed explanation of the verdict, referencing specific lines of code and the ADR.")

def evaluate_code(state: ArchivistState) -> dict:
    print("\n--- EVALUATION AGENT: Cross-referencing Code vs ADRs ---")
    
    diff = state.get("pr_diff", "")
    adrs = state.get("relevant_adrs", "")
    
    if "No specific architectural rules found" in adrs:
        print("No relevant ADRs to enforce. Passing PR.")
        return {"violation_found": False, "evaluation_result": "No applicable ADRs found. Code looks good."}

    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(EvaluationVerdict)
    
    prompt = f"""
    You are an expert Staff Engineer acting as an automated architectural governance engine.
    Review the following Pull Request Code Diff against the provided Architecture Decision Records (ADRs).
    
    Your job is to determine IF the code violates any of the strict rules laid out in the ADRs.
    Be objective. Do not complain about general code quality or syntax; ONLY enforce the ADR rules.
    
    --- ADRs (The Rules) ---
    {adrs}
    
    --- PR Code Diff ---
    {diff[:25000]}
    """
    
    result = structured_llm.invoke(prompt)
    
    print(f"Verdict: {' VIOLATION' if result.violation_found else ' PASS'}")
    
    return {
        "violation_found": result.violation_found,
        "evaluation_result": result.reasoning
    }