from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers.auth  import router as auth_router
from routers.candidates import router as candidates_router
from routers.companies import router as companies_router
from routers.jobs import router as jobs_router
from routers.applications import router as applications_router
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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

@app.get("/")
def root():
    return {"message": "Hello World"}
