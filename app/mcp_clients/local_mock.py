import os
import glob

async def get_mock_adrs(intents: list[str]) -> str:
    """
    Reads all architectural rules from the ADR directory in the user's repository.
    """
    print("[KNOWLEDGE] Scanning local repository for ADRs...")
    
    workspace = os.getenv("GITHUB_WORKSPACE", ".")
    adr_dir = os.path.join(workspace, "ADR")
    
    if not os.path.exists(adr_dir):
        print(f"Directory not found: {adr_dir}")
        return "No specific architectural rules found."
        
    adrs = []

    for filepath in glob.glob(os.path.join(adr_dir, "*.md")):
        with open(filepath, "r") as f:
            adrs.append(f"# File: {os.path.basename(filepath)}\n{f.read()}")
            
    if not adrs:
        return "No specific architectural rules found."
        
    return "\n\n---\n\n".join(adrs)