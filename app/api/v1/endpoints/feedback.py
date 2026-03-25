import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.tools.feedback import record_feedback

logger = logging.getLogger(__name__)

router = APIRouter()

class FeedbackRequest(BaseModel):
    messageId: str
    rating: str
    comment: str = None

@router.post("/feedback")
async def feedback(request: FeedbackRequest, fast_request: Request):
    user_email = fast_request.headers.get("X-Goog-Authenticated-User-Email", "anonymous")
    if ":" in user_email:
        user_email = user_email.split(":")[-1]
    
    logger.info(f"📩 Incoming v1 feedback from {user_email} for {request.messageId}")
    
    try:
        result = record_feedback(
            message_id=request.messageId,
            rating=request.rating,
            user_email=user_email,
            comment=request.comment
        )
        return {"status": "success", "detail": result}
    except Exception as e:
        logger.error(f"❌ Error during v1 feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
