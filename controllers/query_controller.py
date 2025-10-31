from fastapi import APIRouter, Query,Request
router = APIRouter()
from services.query_service import chat_engine


@router.post("/chat")
async def chat_with_your_rag(user_query: str = Query(...),
                             session_id: str = Query(...),
                             user_id: str = Query(...)):

    response = chat_engine.run_chat(user_query, session_id, user_id)  # Call function
    return {"Message": response}
