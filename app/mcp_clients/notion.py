import os
from notion_client import AsyncClient

async def fetch_notion_adrs(intents: list[str]) -> str:
    """Fetches text content from Notion pages in the ADR Database."""
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")
    
    if not token or not db_id:
        return ""

    notion = AsyncClient(auth=token)
    
    # Query the database for active ADRs
    response = await notion.databases.query(
        database_id=db_id,
        filter={
            "property": "Status",
            "select": {"equals": "Accepted"}
        }
    )
    
    compiled_adrs = []
    
    # Extract text from each page's blocks
    for page in response.get("results", []):
        page_id = page["id"]
        blocks = await notion.blocks.children.list(block_id=page_id)
        
        page_text = ""
        for block in blocks.get("results", []):
            block_type = block["type"]
            # Extract plain text from paragraphs, headings, and lists
            if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item"]:
                rich_text = block[block_type].get("rich_text", [])
                text = "".join([t["plain_text"] for t in rich_text])
                page_text += text + "\n"
                
        compiled_adrs.append(page_text)

    return "\n".join(compiled_adrs)