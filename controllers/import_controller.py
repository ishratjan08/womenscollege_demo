from fastapi import Depends,APIRouter
from services.import_service import ingest_html
from fastapi.security import APIKeyHeader
api_key_header = APIKeyHeader(name="x_api_key",auto_error=False)
from utilities.utills import verify_key

router = APIRouter()

@router.get("/import",dependencies=[Depends(verify_key)])
def import_data():
    ingest_html()
    return{"Message":f"You are ready to interact with chat"}
