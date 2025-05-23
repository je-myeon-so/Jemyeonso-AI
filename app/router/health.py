from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(
    tags=["Health Check"],
)
@router.get("/")
def root():
    return {"message": "Jemyeonso APP is running!"}
@router.get("/health", summary="헬스 체크", response_description="서버 상태 OK 여부 반환")
async def health_check():
    return JSONResponse(status_code=200, content={"status": "UP"})