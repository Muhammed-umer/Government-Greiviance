import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from services.api.src.core.config import settings
from services.api.src.routers import auth, petitions, incidents, officer, admin

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Bilingual Tamil Nadu Government Grievance Portal API"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # allow all for local dev & mobile PWA
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static directory for file uploads / mock TTS audio
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/audio_placeholders", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API Routers
app.include_router(auth.router)
app.include_router(petitions.router)
app.include_router(incidents.router)
app.include_router(officer.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "ai_adapters": {
            "stt": settings.AI_STT_PROVIDER,
            "tts": settings.AI_TTS_PROVIDER,
            "routing": settings.AI_ROUTING_PROVIDER,
            "duplicate": settings.AI_DUPLICATE_PROVIDER
        }
    }
