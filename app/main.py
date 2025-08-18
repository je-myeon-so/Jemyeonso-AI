from fastapi import FastAPI
from app.router import health, interview, resume, s3_connection, pii_check
from app.core.question_cache import question_cache
from app.interview.prompt_loader import preload_prompts
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting application...")

    preload_prompts()
    print("Prompts preloaded")
    await question_cache.start_background_cleanup()
    print("Cache cleanup task started")
    print("Application startup complete")
    yield
    
    print("🔽 Shutting down application...")
    await question_cache.stop_background_cleanup()
    print("✅ Application shutdown complete")

app = FastAPI(
    title="Jemyeonso API",
    description="이력서 기반 면접 준비 시스템",
    version="1.5.0",
    lifespan=lifespan
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
