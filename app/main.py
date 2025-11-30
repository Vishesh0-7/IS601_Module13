# app/main.py
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging, time
from app import operations as ops
from app import crud, schemas
from app.database import get_db, Base, engine
from app.routes_users import router as users_router
from app.routes_calculations import router as calculations_router
from app.routes_auth import router as auth_router

# ----- Logging setup -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
log = logging.getLogger("calculator")

app = FastAPI(title="FastAPI Calculator", version="1.0.0")

# Enable CORS for frontend pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(calculations_router)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    """Create database tables if they don't exist."""
    Base.metadata.create_all(bind=engine)
    log.info("Database tables created/verified")

# Static UI
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount frontend pages
import os
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    log.info("REQ %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
        elapsed = (time.time() - start) * 1000
        log.info("RES %s %s -> %s in %.2f ms", request.method, request.url.path, response.status_code, elapsed)
        return response
    except Exception as e:
        log.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/", response_class=HTMLResponse)
def index():
    """Landing page - shows login/register or redirects to calculator if authenticated."""
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/add")
def add(a: float, b: float):
    return {"result": ops.add(a, b)}

@app.get("/sub")
def sub(a: float, b: float):
    return {"result": ops.sub(a, b)}

@app.get("/mul")
def mul(a: float, b: float):
    return {"result": ops.mul(a, b)}

@app.get("/div")
def div(a: float, b: float):
    try:
        return {"result": ops.div(a, b)}
    except ZeroDivisionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/calc")
def calc(op: str, a: float, b: float):
    op = op.lower()
    funcs = {"add": ops.add, "sub": ops.sub, "mul": ops.mul, "div": ops.div}
    if op not in funcs:
        raise HTTPException(status_code=400, detail="Unsupported operation")
    try:
        return {"op": op, "result": funcs[op](a, b)}
    except ZeroDivisionError as e:
        raise HTTPException(status_code=400, detail=str(e))
