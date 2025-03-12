from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, strava, activities
from app.database import engine
from app.models import user, activity
import uvicorn
import traceback

# Tạo bảng trong DB
user.Base.metadata.create_all(bind=engine)
activity.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Strava Integration API",
    description="API backend cho ứng dụng tích hợp với Strava",
    version="1.0.0",
    debug=True  # Bật chế độ debug
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(strava.router)
app.include_router(activities.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Strava Integration API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
