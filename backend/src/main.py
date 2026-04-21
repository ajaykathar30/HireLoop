from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.auth.router import router as auth_router

app = FastAPI(
    title="HireLoop API",
    description="AI Recruitment assistance Pipeline",
    version="1.0.0"
)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend dev server
    allow_credentials=True,   # required for cookies to work cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Hello World"}