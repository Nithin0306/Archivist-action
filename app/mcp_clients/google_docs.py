import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

GDOCS_FOLDER_ID = os.getenv("GDOCS_ADR_FOLDER_ID")

def get_gdocs_service():
    scopes = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/documents.readonly']
    creds = Credentials.from_service_account_file('google_credentials.json', scopes=scopes)
    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)
    return drive_service, docs_service

def extract_text_from_doc(docs_service, document_id):
    """Parses the nested Google Doc JSON structure to extract plain text."""
    doc = docs_service.documents().get(documentId=document_id).execute()
    content = doc.get('body').get('content')
    
    text = ""
    for element in content:
        if 'paragraph' in element:
            elements = element.get('paragraph').get('elements')
            for elem in elements:
                if 'textRun' in elem:
                    text += elem.get('textRun').get('content')
    return text

async def fetch_gdocs_adrs(intents: list[str]) -> str:
    """Finds ADR docs in a Drive folder and extracts their text."""
    if not GDOCS_FOLDER_ID or not os.path.exists('google_credentials.json'):
        return ""
        
    drive_service, docs_service = get_gdocs_service()
    
    query = f"'{GDOCS_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.document'"
    results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    
    compiled_adrs = []
    
    for item in items:
        doc_text = extract_text_from_doc(docs_service, item['id'])
        compiled_adrs.append(f"# {item['name']}\n{doc_text}")
        
    return "\n\n".join(compiled_adrs)