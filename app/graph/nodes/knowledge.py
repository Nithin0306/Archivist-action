import asyncio
from app.graph.state import ArchivistState
from app.mcp_clients.local_md import fetch_local_adrs
from app.mcp_clients.notion import fetch_notion_adrs
from app.mcp_clients.google_docs import fetch_gdocs_adrs

async def fetch_knowledge(state: ArchivistState) -> dict:
    print("\n--- KNOWLEDGE AGENT: Searching for ADRs ---")
    
    intents = state.get("extracted_intents", [])
    
    if not intents:
        print("No specific domains identified. Skipping ADR search.")
        return {"relevant_adrs": "No specific architectural rules found for these changes."}
    
    results = await asyncio.gather(
        fetch_local_adrs(intents),
        fetch_notion_adrs(intents),
        fetch_gdocs_adrs(intents)
    )
    
    local_rules, notion_rules, gdocs_rules = results
    
    compiled_knowledge = ""
    
    if local_rules:
        compiled_knowledge += f"### Local Repository Rules ###\n{local_rules}\n\n"
    if notion_rules:
        compiled_knowledge += f"### Notion Wiki Rules ###\n{notion_rules}\n\n"
    if gdocs_rules:
        compiled_knowledge += f"### Google Docs Rules ###\n{gdocs_rules}\n\n"
        
    if not compiled_knowledge.strip():
        compiled_knowledge = "No specific architectural rules found for these changes across any connected systems."
    
    snippet = compiled_knowledge[:100].replace('\n', ' ') + "..."                
    print(f"Retrieved Context: {snippet}")               
    
    return {"relevant_adrs": compiled_knowledge.strip()}