import os
import sqlite3
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "secure_vault"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    conn = sqlite3.connect("vault.db")
    conn.row_factory = sqlite3.Row
    return conn

def log_action(user_email: str, action: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO audit_logs (user_email, action) VALUES (?, ?)", (user_email, action))
    conn.commit()
    conn.close()

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/register")
def register(request: Request, email: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email.strip().lower(), password))
        conn.commit()
        log_action(email, "USER_REGISTERED")
        return RedirectResponse(url=f"/dashboard?email={email}", status_code=303)
    except sqlite3.IntegrityError:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Email already registered. Please login."})
    finally:
        conn.close()

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email.strip().lower(), password))
    user = cursor.fetchone()
    conn.close()
    if user:
        log_action(email, "LOGIN_SUCCESS")
        return RedirectResponse(url=f"/dashboard?email={email}", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, email: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE owner_email = ? OR shared_with LIKE ?", (email, f"%{email}%"))
    docs = cursor.fetchall()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 10")
    logs = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "email": email, "documents": docs, "logs": logs})

@app.post("/upload")
async def upload_file(email: str = Form(...), file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO documents (filename, owner_email) VALUES (?, ?)", (file.filename, email))
    conn.commit()
    conn.close()
    
    log_action(email, f"UPLOADED_{file.filename}")
    return RedirectResponse(url=f"/dashboard?email={email}", status_code=303)

@app.post("/share")
def share_file(email: str = Form(...), doc_id: int = Form(...), share_with: str = Form(...)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ? AND owner_email = ?", (doc_id, email))
    doc = cursor.fetchone()
    if not doc:
        conn.close()
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    updated_shares = (doc["shared_with"] + f",{share_with.strip().lower()}").strip(",")
    cursor.execute("UPDATE documents SET shared_with = ? WHERE id = ?", (updated_shares, doc_id))
    conn.commit()
    conn.close()
    
    log_action(email, f"SHARED_DOC_{doc_id}_WITH_{share_with}")
    return RedirectResponse(url=f"/dashboard?email={email}", status_code=303)

@app.get("/download/{doc_id}")
def download(doc_id: int, email: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    doc = cursor.fetchone()
    conn.close()
    
    if not doc or (doc["owner_email"] != email and email not in doc["shared_with"].split(",")):
        log_action(email, f"UNAUTHORIZED_ACCESS_DOC_{doc_id}")
        raise HTTPException(status_code=403, detail="Forbidden")
    
    log_action(email, f"DOWNLOADED_DOC_{doc_id}")
    file_path = os.path.join(UPLOAD_DIR, doc["filename"])
    return FileResponse(file_path, filename=doc["filename"])