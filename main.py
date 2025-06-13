from fastapi import FastAPI
from app.router import health, interview, resume, s3_connection, pii_check
from app.core.question_cache import cache_lifespan
# from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Jemyeonso API",
    description="이력서 기반 면접 준비 시스템",
    version="1.0.0",
    lifespan=cache_lifespan
)

app.include_router(interview.router, prefix="/api/ai")
app.include_router(resume.router, prefix="/api/ai")
app.include_router(s3_connection.router)
app.include_router(pii_check.router, prefix="/api/ai")
app.include_router(health.router)

if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0"
    port = 8000
    uvicorn.run(app, host=host, port=port)

