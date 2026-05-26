import os
from .local_mock import get_mock_adrs
from .notion import fetch_notion_adrs
from .google_docs import fetch_gdocs_adrs

async def get_all_adrs(intents: list[str]) -> str:
    """Combines ADRs from all configured sources."""
    print("[KNOWLEDGE] Aggregating architectural rules...")
    
    adrs = []
    
    local_adrs = await get_mock_adrs(intents)
    if local_adrs and "No specific architectural rules found" not in local_adrs:
        adrs.append(local_adrs)

    if os.getenv("NOTION_TOKEN") and os.getenv("NOTION_DATABASE_ID"):
        try:
            notion_adrs = await fetch_notion_adrs(intents)
            if notion_adrs: 
                print("[KNOWLEDGE] Successfully pulled Notion ADRs.")
                adrs.append(notion_adrs)
        except Exception as e:
            print(f"[KNOWLEDGE] Notion fetch failed: {e}")

    if os.getenv("GDOCS_ADR_FOLDER_ID"):
        try:
            gdocs_adrs = await fetch_gdocs_adrs(intents)
            if gdocs_adrs: 
                print("[KNOWLEDGE] Successfully pulled Google Docs ADRs.")
                adrs.append(gdocs_adrs)
        except Exception as e:
            print(f"[KNOWLEDGE] GDocs fetch failed: {e}")

    if not adrs:
        return "No specific architectural rules found."
    
    return "\n\n---\n\n".join(adrs)