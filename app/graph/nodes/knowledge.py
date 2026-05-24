from app.graph.state import ArchivistState
from app.mcp_clients.notion import search_adrs

def fetch_knowledge(state: ArchivistState) -> dict:
    print("\n--- KNOWLEDGE AGENT: Searching for ADRs ---")
    
    intents = state.get("extracted_intents", [])
    
    if not intents:
        print("No specific domains identified. Skipping ADR search.")
        return {"relevant_adrs": "No specific architectural rules found for these changes."}
    
    adrs = search_adrs(intents)       # Fetches the rules using MCP tool
    
    snippet = adrs[:100].replace('\n', ' ') + "..."                # Just to keep the terminal clean
    print(f"Retrieved Context: {snippet}")               
    
    return {"relevant_adrs": adrs}     # Updates the state