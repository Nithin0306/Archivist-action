from .notion import fetch_notion_adrs
from .google_docs import fetch_gdocs_adrs

async def get_all_adrs(intents: list[str]) -> str:
    """Fetches ADRs from all configured sources and combines them."""

    adrs = []
    
    try:
        notion_adrs = await fetch_notion_adrs(intents)
        if notion_adrs: adrs.append(notion_adrs)
    except Exception as e:
        print(f"Notion fetch failed: {e}")

    try:
        gdocs_adrs = await fetch_gdocs_adrs(intents)
        if gdocs_adrs: adrs.append(gdocs_adrs)
    except Exception as e:
        print(f"GDocs fetch failed: {e}")

    if not adrs:
        return "No specific architectural rules found."
    
    return "\n\n---\n\n".join(adrs)