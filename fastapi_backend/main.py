from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, auth
from services.origin_service import origin_service
from models.schemas import HealthResponse
from config import settings

app = FastAPI(
    title="CampusAI Assistant API",
    description="AI-powered assistant for campus freshers",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to CampusAI Assistant API!",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API and Node microservice health"""
    node_health = await origin_service.check_health()
    
    return HealthResponse(
        status="ok",
        service="CampusAI FastAPI Backend",
        node_service_connected="status" in node_health and node_health["status"] == "ok"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.api_port)