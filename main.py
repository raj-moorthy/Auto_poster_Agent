import os
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import UPLOAD_DIR
from db import SessionLocal, init_db, Post, Lead
from agent import run_agent_create_and_post

# --- Init DB & folders ---
init_db()
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# --- Static & media ---
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# --- HTML pages (no app.mount('/')!) ---

@app.get("/")
def home():
    return FileResponse("templates/index.html")


@app.get("/dashboard.html")
def dashboard():
    return FileResponse("templates/dashboard.html")


@app.get("/lead_form.html")
def lead_form():
    return FileResponse("templates/lead_form.html")


@app.get("/upload.html")
def upload_page():
    return FileResponse("templates/upload.html")


@app.get("/post_preview.html")
def preview_page():
    return FileResponse("templates/post_preview.html")


# --- Upload & media list ---

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    save_path = UPLOAD_DIR / file.filename
    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)
    return {
        "status": "ok",
        "filename": file.filename,
        "path": save_path.relative_to(UPLOAD_DIR.parent).as_posix(),
    }


@app.get("/media/list")
def media_list():
    files = []
    for fname in os.listdir(UPLOAD_DIR):
        fpath = UPLOAD_DIR / fname
        if fpath.is_file():
            files.append(fname)
    return {"files": files}


# --- Agent: create & post ---

@app.post("/create_and_post")
async def create_and_post(
    prompt: str = Form(...),
    platforms: str = Form(...),
    scheduled_time: Optional[str] = Form(None),
):
    platforms_list = [
        p.strip().lower() for p in platforms.split(",") if p.strip()
    ]
    result = run_agent_create_and_post(prompt, platforms_list, scheduled_time)
    return JSONResponse(result)


# --- Posts for dashboard ---

@app.get("/posts")
def get_posts():
    db = SessionLocal()
    try:
        rows = db.query(Post).order_by(Post.id.desc()).limit(200).all()
        out = []
        for p in rows:
            out.append(
                {
                    "id": p.id,
                    "platform": p.platform,
                    "caption": p.caption,
                    "status": p.status,
                    "scheduled_time": str(p.scheduled_time)
                    if getattr(p, "scheduled_time", None)
                    else None,
                    "posted_at": str(p.posted_at)
                    if getattr(p, "posted_at", None)
                    else None,
                    "platform_post_id": p.platform_post_id,
                    "error": getattr(p, "error", None),
                }
            )
        return {"posts": out}
    except Exception as e:
        return JSONResponse(
            {"posts": [], "error": f"Internal Server Error: {e}"},
            status_code=200,
        )
    finally:
        db.close()


# --- Leads API ---

class LeadCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    service: Optional[str] = None
    message: Optional[str] = None


@app.post("/save_lead")
def save_lead(lead: LeadCreate):
    db = SessionLocal()
    try:
        db_lead = Lead(
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            service=lead.service,
            message=lead.message,
        )
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        return {
            "status": "ok",
            "lead": {
                "id": db_lead.id,
                "name": db_lead.name,
                "email": db_lead.email,
                "phone": db_lead.phone,
                "service": db_lead.service,
                "message": db_lead.message,
                "created_at": str(db_lead.created_at),
            },
        }
    finally:
        db.close()


@app.get("/leads")
def get_leads():
    db = SessionLocal()
    try:
        rows = db.query(Lead).order_by(Lead.id.desc()).limit(200).all()
        out = []
        for l in rows:
            out.append(
                {
                    "id": l.id,
                    "name": l.name,
                    "email": l.email,
                    "phone": l.phone,
                    "service": l.service,
                    "message": l.message,
                    "created_at": str(l.created_at),
                }
            )
        return {"leads": out}
    finally:
        db.close()
