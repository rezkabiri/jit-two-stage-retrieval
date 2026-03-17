# app/main.py
import os
import sys
import logging
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from app.agent import root_agent
from app.tools.feedback import record_feedback, record_conversation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🚀 STARTING AGENT SERVICE")

app = FastAPI()

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
        enriched_query = f"User: {user_email}\nQuery: {request.query}"
        
        # Pydantic AI/ADK Agents typically use run_sync or run
        if hasattr(root_agent, "run_sync"):
            result = root_agent.run_sync(enriched_query)
            response_text = result.data if hasattr(result, "data") else str(result)
        else:
            # Fallback for older versions
            result = await root_agent.run(enriched_query) if hasattr(root_agent, "run") else root_agent(enriched_query)
            response_text = getattr(result, "data", str(result))
            
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
