from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import ENCODERS_BY_TYPE
import numpy as np
from contextlib import asynccontextmanager

from routers.auth  import router as auth_router
from routers.candidates import router as candidates_router
from routers.companies import router as companies_router
from routers.jobs import router as jobs_router
from routers.applications import router as applications_router
from routers.interviews import router as interviews_router
from routers.notifications import router as notifications_router
from core.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the background scheduler
    start_scheduler()
    yield
    # Shutdown logic (if any) can go here

app = FastAPI(
    title="HireLoop API",
    description="AI Recruitment assistance Pipeline",
    version="1.0.0",
    lifespan=lifespan
)

# ─── CORS ─────────────────────────────────────────────────────────────────────

# Register NumPy encoder globally for all responses
ENCODERS_BY_TYPE[np.ndarray] = lambda obj: obj.tolist()

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="http://(localhost|127\.0\.0\.1):[0-9]+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(candidates_router)
app.include_router(companies_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(interviews_router)
app.include_router(notifications_router)

@app.get("/")
def root():
    return {"message": "Hello World"}
