from fastapi import FastAPI
from router import health
app = FastAPI()
@app.get("/")
def root():
    return {"message": "Jemyeonso APP is running!"}

app.include_router(health.router)

if __name__ == "__main__":
    import uvicorn
    host = "0.0.0.0"
    port = 8000
    uvicorn.run(app, host=host, port=port)

