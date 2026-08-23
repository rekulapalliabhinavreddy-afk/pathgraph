from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .config import CORS_ORIGINS
from .db import driver, close_driver
from .models import ProfileRequest
from .repository import GraphRepository
from pathlib import Path


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_driver()


app = FastAPI(title="PathGraph API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = GraphRepository(driver) if driver else None

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


def db_or_503():
    if repo is None:
        raise HTTPException(status_code=503, detail="Graph database is not configured. Add COGNODB_URI and COGNODB_PASSWORD.")
    try:
        if not repo.health():
            raise RuntimeError("health check failed")
    except Exception:
        raise HTTPException(status_code=503, detail="Graph database is currently unreachable. Please try again shortly.")
    return repo


@app.get("/api/health")
def health():
    if repo is None:
        return JSONResponse(status_code=503, content={"status": "database_not_configured"})
    try:
        repo.health()
        return {"status": "ok"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "database_unreachable"})


@app.get("/api/roles")
def get_roles():
    try:
        return db_or_503().roles()
    except HTTPException:
        raise
    except Exception as exc:
        print("ROLES ERROR:", repr(exc))
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/skills")
def get_skills():
    try:
        return db_or_503().skills()
    except HTTPException:
        raise
    except Exception as exc:
        print("SKILLS ERROR:", repr(exc))
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.post("/api/profile")
def get_profile(payload: ProfileRequest):
    try:
        result = db_or_503().profile(payload.role_slug, payload.current_skills)
        if result is None:
            raise HTTPException(status_code=404, detail="Role not found.")
        result["related_roles"] = repo.related_roles(payload.role_slug)
        result["technologies"] = repo.technologies(payload.role_slug)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to analyze the selected career path.") from exc


@app.get("/api/graph/{role_slug}")
def get_graph(role_slug: str):
    try:
        return db_or_503().technologies(role_slug)
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(status_code=500, detail="Unable to load graph neighborhood.") from exc


@app.get("/")
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/app.js")
def frontend_js():
    return FileResponse(FRONTEND_DIR / "app.js", media_type="application/javascript")

@app.get("/styles.css")
def frontend_css():
    return FileResponse(FRONTEND_DIR / "styles.css", media_type="text/css")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
