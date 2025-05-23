from fastapi import FastAPI
from app.router import health, interview
# from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Jemyeonso API",
    description="이력서 기반 면접 준비 시스템",
    version="1.0.0"
)

# 🔒 [CORS 설정 안내]
# CORS(Cross-Origin Resource Sharing)는 브라우저 보안 정책으로 인해,
# 다른 출처(예: 프론트엔드가 localhost:3000, 백엔드는 8000 포트일 경우) 간의 요청을 차단합니다.
# 이 미들웨어는 특정 Origin에서의 접근을 허용하는 설정입니다.
# 현재는 모든 도메인에서 요청을 허용하도록 설정되어 있으나, 배포 시에는 특정 도메인만 허용해야 합니다.

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 개발용: 모든 도메인 허용. 배포 시 수정 필요 (예: ["https://frontend.example.com"])
#     allow_credentials=True,  # 인증 정보(쿠키 등) 포함 허용
#     allow_methods=["*"],  # 모든 HTTP 메서드 허용
#     allow_headers=["*"],  # 모든 헤더 허용
# )

app.include_router(interview.router, prefix="/api/ai")

app.include_router(health.router)

if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0"
    port = 8000
    uvicorn.run(app, host=host, port=port)

