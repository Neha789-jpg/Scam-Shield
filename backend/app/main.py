from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="TrustCheck API",
    description="Explainable risk checks for online sellers.",
    version="0.1.0",
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "trustcheck-api"}
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(router)