from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import sqlite3
import uvicorn
from lstm_in_use import load_and_forecast 
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="super_secret_key")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=os.path.join(ROOT_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(ROOT_DIR, "templates"))

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()


def get_current_user(request: Request):
    return request.session.get("user")


@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/index")
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        request.session["user"] = username
        return RedirectResponse(url="/index", status_code=303)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials!"})


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_user(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return RedirectResponse(url="/", status_code=303)
    except sqlite3.IntegrityError:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists!"})


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")


@app.get("/index", response_class=HTMLResponse)
def index(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.post("/predict")
async def predict(request: Request, days: int = Form(...), graph_type: str = Form(...)):
    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/", status_code=303)

    try:
        # Call your LSTM model function
        graph = load_and_forecast(n_days=days, graph_type=graph_type)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "graph": graph,
            "graph_type": graph_type,
            "days": days
        })
    
    except Exception as e:
        # Catch errors and display them in the frontend
        return templates.TemplateResponse("index.html", {
            "request": request,
            "user": user,
            "error": f"Error while predicting: {str(e)}"
        })



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
