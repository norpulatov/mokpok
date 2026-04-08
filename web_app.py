from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from database import AsyncSessionLocal, Movie
from config import WEB_PASSWORD, CHANNEL_ID
from utils import get_channel_link
import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# Simple auth for admin
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_password = secrets.compare_digest(credentials.password, WEB_PASSWORD)
    if not correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri parol",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Movie).order_by(Movie.movie_number.desc()).limit(50))
    movies = result.scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "movies": movies})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = "", db: AsyncSession = Depends(get_db)):
    movies = []
    if q:
        if q.isdigit():
            result = await db.execute(select(Movie).where(Movie.movie_number == int(q)))
            movie = result.scalar_one_or_none()
            if movie:
                movies = [movie]
        else:
            result = await db.execute(select(Movie).where(Movie.title.ilike(f"%{q}%")).order_by(Movie.movie_number).limit(50))
            movies = result.scalars().all()
    return templates.TemplateResponse("search.html", {"request": request, "movies": movies, "query": q})

@app.get("/movie/{number}", response_class=HTMLResponse)
async def movie_detail(request: Request, number: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Movie).where(Movie.movie_number == number))
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="Kino topilmadi")
    watch_url = get_channel_link(movie.channel_chat_id, movie.channel_message_id)
    return templates.TemplateResponse("movie_detail.html", {"request": request, "movie": movie, "watch_url": watch_url})

# Admin routes
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, db: AsyncSession = Depends(get_db), _: bool = Depends(verify_admin)):
    result = await db.execute(select(Movie).order_by(Movie.movie_number.desc()))
    movies = result.scalars().all()
    return templates.TemplateResponse("admin.html", {"request": request, "movies": movies})

@app.post("/admin/edit/{movie_id}")
async def admin_edit(movie_id: int, title: str = Form(...), description: str = Form(...),
                     db: AsyncSession = Depends(get_db), _: bool = Depends(verify_admin)):
    await db.execute(update(Movie).where(Movie.id == movie_id).values(title=title, description=description))
    await db.commit()
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/delete/{movie_id}")
async def admin_delete(movie_id: int, db: AsyncSession = Depends(get_db), _: bool = Depends(verify_admin)):
    await db.execute(delete(Movie).where(Movie.id == movie_id))
    await db.commit()
    return RedirectResponse("/admin", status_code=303)

@app.post("/admin/add", response_class=HTMLResponse)
async def admin_add(request: Request, title: str = Form(...), description: str = Form(...),
                    file_id: str = Form(None), db: AsyncSession = Depends(get_db), _: bool = Depends(verify_admin)):
    # Note: actual file upload via web not implemented due to process separation; use bot for uploads.
    if not file_id:
        return templates.TemplateResponse("admin.html", {"request": request, "error": "File ID kerak"}, status_code=400)
    # You could send video to channel using bot's API here, but for simplicity we skip.
    return RedirectResponse("/admin", status_code=303)