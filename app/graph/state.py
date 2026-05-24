from typing import TypedDict, List, Optional

class ArchivistState(TypedDict):
    # Input metadata
    repo_full_name: str
    pr_number: int
    
    # Context agent 
    pr_diff: str
    extracted_intents: List[str] 
    
    # Knowledge agent 
    relevant_adrs: str
    
    # Evaluation agent
    evaluation_result: str
    violation_found: bool
    
    # Handoff agent
    final_comment: Optional[str]