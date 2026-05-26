from typing import List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graph.state import ArchivistState
from app.utils.config import LLM_MODEL

class MetadataAnalysis(BaseModel):
    score: int = Field(description="Score from 0 to 10 evaluating the detail and architectural clarity of the PR description and PR title.")
    extracted_intents: List[str] = Field(description="List of architectural domains guessed from the text and file paths. Empty if the text is too vague.")
    reasoning: str = Field(description="Why this score was given.")

def match_metadata(state: ArchivistState) -> dict:
    print("\n--- METADATA MATCHER: Evaluating PR Quality ---")
    
    title = state.get("pr_title", "")
    body = state.get("pr_body", "")
    files = state.get("pr_file_paths", [])
    
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0)
    structured_llm = llm.with_structured_output(MetadataAnalysis)
    
    prompt = f"""
    Evaluate the quality and detail of this Pull Request metadata.
    
    - Score 8-10: The PR title/body is highly detailed, clearly explaining architectural changes, and aligns with the file paths. We can evaluate this without reading the code.
    - Score 0-7: This is a "dump message" (e.g., "fixed bugs", "updates", empty body) OR the text doesn't give enough context to know what the code actually does. We MUST read the raw code.
    
    PR Title: {title}
    PR Body: {body}
    Files Changed: {files}
    """
    
    result = structured_llm.invoke(prompt)
    print(f"Quality Score: {result.score}/10 ({result.reasoning})")
    
    # If the score is high, intents are extracted here. If low, leaving it empty
    intents = result.extracted_intents if result.score >= 8 else []
    
    return {
        "metadata_score": result.score,
        "extracted_intents": intents
    }