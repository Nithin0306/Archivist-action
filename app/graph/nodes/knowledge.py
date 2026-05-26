from app.graph.state import ArchivistState
# from app.mcp_clients.knowledge_base import get_all_adrs         # (Notion + GDocs)
from app.mcp_clients.local_mock import get_mock_adrs as get_all_adrs  # MOCK (Local md)

async def fetch_knowledge(state: ArchivistState) -> dict:
    print("\n--- KNOWLEDGE AGENT: Searching for ADRs ---")
    
    intents = state.get("extracted_intents", [])
    
    if not intents:
        print("No specific domains identified. Skipping ADR search.")
        return {"relevant_adrs": "No specific architectural rules found for these changes."}
    
    adrs = await get_all_adrs(intents)      # Fetches the rules using MCP tool
    
    snippet = adrs[:100].replace('\n', ' ') + "..."                # Just to keep the terminal clean
    print(f"Retrieved Context: {snippet}")               
    
    return {"relevant_adrs": adrs}     # Updates the state