from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ray
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request  
from agents import (
    schedule_meeting,
    reschedule_meeting,
    learn_from_feedback,
    email_handler,
    initialize_history_id,
    fetch_new_emails
)
import sqlite3
import asyncio
import threading
import time
import logging
import os
from typing import List
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import random 

# Google Docs & Drive Integration
from googleapiclient.http import MediaFileUpload

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]

# Initialize Ray once
if not ray.is_initialized():
    ray.init(ignore_reinit_error=True)

app = FastAPI(title="AI Multi-Agent Calendar Scheduler with Email Integration")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"]  # Allows all headers
)

# Define request models
class ScheduleRequest(BaseModel):
    text: str

class RescheduleRequest(BaseModel):
    text: str

class CancelRequest(BaseModel):
    meeting_id: int

class FeedbackRequest(BaseModel):
    meeting_id: int
    rating: int
    comments: str

class SentimentAnalysis(BaseModel):
    msg_id: str
    sentiment: str
    confidence: float
    priority: str
    processed_at: datetime
    subject: str
    body: str

class Task(BaseModel):
    title: str
    project: str
    assignee: List[str]
    dueDate: str
    status: str
    created_at: datetime

class TaskAnalysis(BaseModel):
    msg_id: str
    tasks: List[Task]
    processed_at: datetime

class GoogleDocsRequest(BaseModel):
    title: str
    content: str

class GoogleDriveUploadRequest(BaseModel):
    file_path: str
    mime_type: str

class GoogleDocsModifyRequest(BaseModel):
    document_id: str
    content: str
    index: int = 1  # Default to insert at the beginning

@app.post("/modify_google_doc")
async def modify_google_doc(request: GoogleDocsModifyRequest):
    """Modify an existing Google Doc by inserting new content."""
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build("docs", "v1", credentials=creds)
        
        # Create the request body to insert text at the specified index
        requests = [{
            'insertText': {
                'location': {'index': request.index},
                'text': request.content
            }
        }]
        
        # Execute the batchUpdate request
        service.documents().batchUpdate(
            documentId=request.document_id,
            body={'requests': requests}
        ).execute()
        
        return {"message": "Google Doc modified successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Google Docs API
@app.post("/create_google_doc")
async def create_google_doc(request: GoogleDocsRequest):
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build("docs", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)
        
        # Create the document
        document = service.documents().create(body={"title": request.title}).execute()
        doc_id = document.get("documentId")
        
        # Insert content
        requests = [{"insertText": {"location": {"index": 1}, "text": request.content}}]
        service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
        
        # Get document link
        doc_link = f"https://docs.google.com/document/d/{doc_id}/edit"
        
        # Retry getting thumbnail up to 3 times with a delay
        max_retries = 3
        thumbnail = None
        
        for attempt in range(max_retries):
            # Get document metadata including thumbnail
            file_metadata = drive_service.files().get(
                fileId=doc_id, 
                fields="id, name, thumbnailLink, webViewLink"
            ).execute()
            
            thumbnail = file_metadata.get("thumbnailLink")
            if thumbnail:
                break
                
            # Wait before retrying (increasing delay with each attempt)
            await asyncio.sleep((attempt + 1) * 1)
        
        if not thumbnail:
            # If still no thumbnail, use a default Google Docs icon
            thumbnail = "https://drive-thirdparty.googleusercontent.com/128/type/application/vnd.google-apps.document"
        
        return {
            "document_id": doc_id,
            "title": request.title,
            "link": doc_link,
            "thumbnail": thumbnail,
            "message": "Google Doc created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Google Drive API
@app.post("/upload_to_drive")
async def upload_to_drive(request: GoogleDriveUploadRequest):
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        service = build("drive", "v3", credentials=creds)
        file_metadata = {"name": os.path.basename(request.file_path)}
        media = MediaFileUpload(request.file_path, mimetype=request.mime_type)
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return {"file_id": file.get("id"), "message": "File uploaded to Google Drive successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API Endpoints
@app.get("/tasks", response_model=List[Task])
async def get_tasks():
    """Get all tasks extracted from emails."""
    try:
        conn = sqlite3.connect('scheduler.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT msg_id, title, project, assignee, due_date, status, created_at 
            FROM tasks 
            ORDER BY created_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        names = ["Tabish Shaikh", "Riva Rodrigues", "Nirmitee Sarode"]
        
        return [
            Task(
                title=row[1],
                project=row[2],
                assignee=[random.choice(names)],
                dueDate=row[4],
                status=row[5],
                created_at=datetime.fromisoformat(row[6])
            )
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sentiment/emails", response_model= List[SentimentAnalysis])
async def get_email_sentiments():
    """Get sentiment analysis results for all processed emails."""
    try:
        conn = sqlite3.connect('scheduler.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT msg_id, sentiment, confidence, priority, processed_at ,subject,body
            FROM sentiment_analysis 
            ORDER BY processed_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            SentimentAnalysis(
                msg_id=row[0],
                sentiment=row[1],
                confidence=row[2],
                priority=row[3],
                processed_at=datetime.fromisoformat(row[4]),
                subject=row[5],
                body=row[6]

            )
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule")
async def schedule(request: ScheduleRequest):
    
    from_email = "rodriguesriva1130@gmail.com"  
    result = await schedule_meeting.remote(request.text, from_email)
    return {"message": result}

@app.post("/reschedule")
async def reschedule(request: RescheduleRequest):
    from_email = "rodriguesriva1130@gmail.com"  
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    result = await reschedule_meeting.remote(request.text, creds,from_email)
    return {"message": result}

@app.post("/cancel")
async def cancel(request: CancelRequest):
    try:
        conn = sqlite3.connect('scheduler.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE meetings
            SET status = 'canceled'
            WHERE id = ?
        ''', (request.meeting_id,))
        conn.commit()
        conn.close()
        return {"message": f"Meeting {request.meeting_id} canceled successfully."}
    except Exception as e:
        logger.error(f"Error canceling meeting: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/feedback")
async def feedback(request: FeedbackRequest):
    result = await learn_from_feedback.remote(request.meeting_id, request.rating, request.comments)
    return {"message": result}

@app.post("/process_emails")
async def process_emails():
    """Endpoint to trigger email processing manually."""
    result = await email_handler.remote()
    return {"message": result}

@app.get("/meetings")
def get_meetings():
    """Fetch all meetings."""
    try:
        conn = sqlite3.connect('scheduler.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM meetings')
        meetings = cursor.fetchall()
        conn.close()
        return {"meetings": meetings}
    except Exception as e:
        logger.error(f"Error fetching meetings: {e}")
        raise HTTPException(status_code=500, detail="Error fetching meetings.")

@app.get("/feedback")
def get_feedback():
    """Fetch all feedback."""
    try:
        conn = sqlite3.connect('scheduler.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM feedback')
        feedback = cursor.fetchall()
        conn.close()
        return {"feedback": feedback}
    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        raise HTTPException(status_code=500, detail="Error fetching feedback.")

@app.get("/meeting/{meeting_id}")
def get_meeting_details(meeting_id: int):
    """Fetch details of a specific meeting."""
    try:
        conn = sqlite3.connect('scheduler.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM meetings WHERE id = ?', (meeting_id,))
        meeting = cursor.fetchone()
        cursor.execute('SELECT * FROM feedback WHERE meeting_id = ?', (meeting_id,))
        feedback = cursor.fetchall()
        conn.close()
        return {"meeting": meeting, "feedback": feedback}
    except Exception as e:
        logger.error(f"Error fetching meeting details: {e}")
        raise HTTPException(status_code=500, detail="Error fetching meeting details.")

# Background Email Processing
def email_processing_loop():
    """Loop to process emails every 5 minutes."""
    while True:
        try:
            result = ray.get(email_handler.remote())
            logger.info(result)
        except Exception as e:
            logger.error(f"Error in background email processing: {e}")
        time.sleep(300)  # Wait for 5 minutes



@app.on_event("startup")
def startup_event():
    """Start background thread for email listener."""
    global LATEST_HISTORY_ID
    try:
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # Check if credentials need refreshing
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    # Save refreshed credentials
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    raise ValueError("Failed to refresh Gmail credentials.")
            else:
                # Need to run authorize.py again
                raise ValueError("Gmail credentials expired. Please run authorize.py to refresh.")

        # Initialize Gmail service
        gmail_service = build('gmail', 'v1', credentials=creds)

        # Initialize History ID
        initialize_history_id(gmail_service)

        # Background email listener
        def email_listener():
            while True:
                try:
                    fetch_new_emails(gmail_service)
                except Exception as e:
                    logger.error(f"Error in email_listener: {e}")
                time.sleep(10)  # Poll every 10 seconds

        listener_thread = threading.Thread(target=email_listener, daemon=True)
        listener_thread.start()

        # Start the periodic email processing loop
        processing_thread = threading.Thread(target=email_processing_loop, daemon=True)
        processing_thread.start()

        logger.info("Started email listener and processing threads.")
    except Exception as e:
        logger.error(f"Error starting email listener thread: {e}")
        # Don't raise here, just log the error to prevent app startup failure
