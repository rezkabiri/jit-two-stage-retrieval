# app/main.py
import os
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from google.adk import App
from app.agent import root_agent
from app.tools.feedback import record_feedback, record_conversation

print("🚀 STARTING ADK AGENT SERVICE")

# Initialize ADK App to properly wrap the agent
adk_app = App(root_agent=root_agent, name="two_stage_rag_app", session_type="in_memory")

# Extract the FastAPI instance from the ADK App
app = adk_app.fastapi_app

class ChatRequest(BaseModel):
    query: str

class FeedbackRequest(BaseModel):
    messageId: str
    rating: str
    comment: str = None

@app.post("/api/chat")
async def chat(request: ChatRequest, fast_request: Request, background_tasks: BackgroundTasks):
    # Extract authenticated user email from IAP headers
    user_email = fast_request.headers.get("X-Goog-Authenticated-User-Email", "anonymous")
    if ":" in user_email:
        user_email = user_email.split(":")[-1]

    try:
        enriched_query = f"User: {user_email}\nQuery: {request.query}"
        
        # Use the adk_app to run the query, which handles context and session properly
        result = await adk_app.run(enriched_query)
        response_text = result.data if hasattr(result, "data") else str(result)
            
        # Log the conversation in the background
        background_tasks.add_task(
            record_conversation, 
            query=request.query, 
            response=response_text, 
            user_email=user_email
        )
        
        return {"response": response_text}
    except Exception as e:
        print(f"Error during chat: {e}")
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
        print(f"Error during feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok", "message": "ADK Agent is online"}

if __name__ == "__main__":
    import uvicorn
    # Use the PORT environment variable provided by Cloud Run
    port = int(os.environ.get("PORT", 8080))
    print(f"📡 Listening on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
