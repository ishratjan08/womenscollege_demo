from fastapi import Depends,HTTPException
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
import os

api_key_header = APIKeyHeader(name="x_api_key",auto_error=False)
load = load_dotenv()
key = os.getenv("API_KEY")

def verify_key(x_api_key: str = Depends(api_key_header)):
    if x_api_key != key:
        raise HTTPException(status_code=401,detail="Invalid key")
    return x_api_key