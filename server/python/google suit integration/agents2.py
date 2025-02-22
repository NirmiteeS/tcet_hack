from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
import os

# Google API Scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]

# Load credentials
CREDENTIALS_FILE = "credentials.json"  # Ensure this file is correctly set up
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)

def create_google_doc(title: str, content: str):
    """Create a new Google Document with the given title and content."""
    service = build('docs', 'v1', credentials=creds)
    doc = service.documents().create(body={"title": title}).execute()
    document_id = doc['documentId']
    
    # Add content to the document
    requests = [{
        'insertText': {
            'location': {'index': 1},
            'text': content
        }
    }]
    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    
    return f"Document created successfully: https://docs.google.com/document/d/{document_id}"

def upload_to_drive(file_path: str, folder_id: str = None):
    """Upload a file to Google Drive."""
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    
    return f"File uploaded successfully: {file.get('webViewLink')}"

def list_drive_files():
    """List files in Google Drive."""
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(pageSize=10, fields="files(id, name, webViewLink)").execute()
    files = results.get('files', [])
    
    return [{"id": f["id"], "name": f["name"], "link": f["webViewLink"]} for f in files]



