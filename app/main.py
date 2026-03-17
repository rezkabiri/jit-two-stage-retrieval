# app/main.py
import os
import sys
import logging
import hashlib
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app.agent import root_agent
from app.tools.feedback import record_feedback, record_conversation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🚀 STARTING AGENT SERVICE")

app = FastAPI()

# Initialize ADK Runner and Session Service
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="rag-app", session_service=session_service, auto_create_session=True)

class ChatRequest(BaseModel):
    query: str

class FeedbackRequest(BaseModel):
    messageId: str
    rating: str
    comment: str = None

@app.post("/api/chat")
async def chat(request: ChatRequest, fast_request: Request, background_tasks: BackgroundTasks):
    user_email = fast_request.headers.get("X-Goog-Authenticated-User-Email", "anonymous")
    if ":" in user_email:
        user_email = user_email.split(":")[-1]

    try:
        # Generate a stable session ID for the user
        session_id = hashlib.md5(user_email.encode()).hexdigest()
        
        response_text = ""
        async for event in runner.run_async(
            user_id=user_email,
            session_id=session_id,
            new_message=types.Content(role="user", parts=[types.Part.from_text(text=request.query)])
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
            
        background_tasks.add_task(
            record_conversation, 
            query=request.query, 
            response=response_text, 
            user_email=user_email
        )
        
        return {"response": response_text}
    except Exception as e:
        logger.error(f"Error during chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def feedback(request: FeedbackRequest, fast_request: Request):
    user_email = fast_request.headers.get("X-Goog-Authenticated-User-Email", "anonymous")
    if ":" in user_email:
        user_email = user_email.split(":")[-1]
    try:
        result = record_feedback(
            message_id=request.messageId,
            rating=request.rating,
            user_email=user_email,
            comment=request.comment
        )
        return {"status": "success", "detail": result}
    except Exception as e:
        logger.error(f"Error during feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
