from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graph.state import ArchivistState

class RelevanceScore(BaseModel):
    score: int = Field(description="Relevance score from 0 to 10")
    reasoning: str = Field(description="One-sentence justification for the score")

def match_metadata(state: ArchivistState) -> dict:
    print("\n--- METADATA MATCHER: Fast Path Scoring ---")
    
    title = state.get("pr_title", "")
    body = state.get("pr_body", "")
    
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(RelevanceScore)
    
    prompt = f"""
    You are an architectural routing gate. Review the Pull Request title and description.
    Score from 0 to 10 how likely this PR modifies core architectural domains (e.g., databases, frontend fetching, microservices, auth).
    
    - Score 8-10: Mentions databases, APIs, data fetching, or core infrastructure.
    - Score 0-3: CSS tweaks, typo fixes, documentation updates, or simple UI changes.
    
    PR Title: {title}
    PR Body: {body}
    """
    
    result = structured_llm.invoke(prompt)
    print(f"Gate Score: {result.score}/10 ({result.reasoning})")
    
    return {"metadata_score": result.score}