from fastapi import APIRouter, Query, UploadFile, File, Form
from services.query_service import chat_engine
from voice.stt import speech_to_text
from voice.tts import text_to_speech
import uuid
import os
router = APIRouter()

# Text based chat
@router.post("/chat")
async def chat_with_your_rag(user_query: str = Query(...),
                             session_id: str = Query(...),
                             user_id: str = Query(...)):
    response = chat_engine.run_chat(user_query, session_id, user_id)
    return {"Message": response}

@router.post("/chat/audio")
async def chat_with_audio(
    audio: UploadFile = File(...),
    session_id: str = Form(..., description="Session ID"),
    user_id: str = Form(..., description="User ID")
):
    try:
        # Create input_audio directory if it doesn't exist
        os.makedirs("input_audio", exist_ok=True)
        
        # Save incoming audio
        temp_audio_path = f"input_audio/{uuid.uuid4()}.wav"
        with open(temp_audio_path, "wb") as f:
            f.write(await audio.read())

        # 1️⃣ Convert Speech to Text
        text_query = speech_to_text(temp_audio_path)
        
        if not text_query or text_query.strip() == "":
            return {
                "text": "",
                "message": "Could not transcribe audio. Please try again.",
                "audio_url": ""
            }

        # 2️⃣ Chat Response
        response_text = chat_engine.run_chat(text_query, session_id, user_id)

        # 3️⃣ Convert Text → Audio (TTS)
        output_audio_path = text_to_speech(response_text)
        
        # Outputs directory is created by tts.py
        if not output_audio_path:
            return {
                "text": text_query,
                "message": response_text,
                "audio_url": ""
            }

        # 4️⃣ Return JSON + Downloadable Audio URL
        # output_audio_path is the filename from tts.py
        audio_filename = output_audio_path if isinstance(output_audio_path, str) else os.path.basename(output_audio_path)
        
        audio_url = f"/response_audio/{audio_filename}"
        print(f"DEBUG: Generated audio URL: {audio_url}")
        
        return {
            "text": text_query,
            "message": response_text,
            "audio_url": audio_url
        }
    except Exception as e:
        return {
            "text": "",
            "message": f"Error processing audio: {str(e)}",
            "audio_url": ""
        }
