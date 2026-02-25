"""
ACE Veriflow — FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import extraction, verification, audit, graph
from app.core.config import settings

app = FastAPI(
    title="ACE — Autonomous Compliance Engine",
    description="Decision support for UL product pre-certification (Veriflow)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extraction.router, prefix="/api/extraction", tags=["extraction"])
app.include_router(verification.router, prefix="/api/verification", tags=["verification"])
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])


@app.get("/")
def root():
    return {
        "service": "ACE — Autonomous Compliance Engine",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/extraction | /api/verification | /api/audit | /api/graph",
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "ace-veriflow"}
