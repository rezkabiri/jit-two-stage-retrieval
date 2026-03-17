# app/main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .agent import root_agent
from .tools.feedback import record_feedback

print("🚀 STARTING ADK AGENT SERVICE")

app = FastAPI()

class ChatRequest(BaseModel):
    query: str

class FeedbackRequest(BaseModel):
    messageId: str
    rating: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # In newer ADK/PydanticAI versions, run_sync or run is used.
        # We will try run_sync first as it's common.
        if hasattr(root_agent, "run_sync"):
            result = root_agent.run_sync(request.query)
            # Pydantic AI uses .data for the response content
            response_text = result.data if hasattr(result, "data") else str(result)
        else:
            # Fallback for other adk versions
            result = root_agent(request.query)
            response_text = getattr(result, "text", str(result))
            
        return {"response": response_text}
    except Exception as e:
        print(f"Error during chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/feedback")
async def feedback(request: FeedbackRequest):
    try:
        result = record_feedback(
            message_id=request.messageId,
            rating=request.rating,
            user_email="anonymous" # Would be pulled from headers in real app via IAP
        )
        return {"status": "success", "detail": result}
    except Exception as e:
        print(f"Error during feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Use the PORT environment variable provided by Cloud Run
    port = int(os.environ.get("PORT", 8080))
    print(f"📡 Listening on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
