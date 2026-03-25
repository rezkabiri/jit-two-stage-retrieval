import os
import logging
import hashlib
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from app.agent import root_agent
from app.tools.feedback import record_conversation

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize ADK Runner and Session Service
# In a production app, these might be injected via dependencies
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name="rag-app", session_service=session_service, auto_create_session=True)

class ChatRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat(request: ChatRequest, fast_request: Request, background_tasks: BackgroundTasks):
    user_email = fast_request.headers.get("X-Goog-Authenticated-User-Email", "anonymous")
    if ":" in user_email:
        user_email = user_email.split(":")[-1]

    logger.info(f"📩 Incoming v1 chat request from {user_email}: {request.query[:100]}...")

    try:
        # Generate a stable session ID for the user
        session_id = hashlib.md5(user_email.encode()).hexdigest()
        
        # Inject the user's identity into the query context for the agent
        user_context = f"[USER IDENTITY: {user_email}]\n\n"
        full_query = user_context + request.query

        response_text = ""
        async for event in runner.run_async(
            user_id=user_email,
            session_id=session_id,
            new_message=types.Content(role="user", parts=[types.Part.from_text(text=full_query)])
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
        
        logger.info(f"✅ Generated v1 response for {user_email} (Length: {len(response_text)})")
            
        background_tasks.add_task(
            record_conversation, 
            query=request.query, 
            response=response_text, 
            user_email=user_email
        )
        
        return {"response": response_text}
    except Exception as e:
        logger.error(f"❌ Error during v1 chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
