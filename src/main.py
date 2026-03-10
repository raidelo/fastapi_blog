from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from .database import Base, engine, get_db
from .models import Post
from .schemas import PostCreate, PostResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), "static")

templates = Jinja2Templates(directory="templates")

type DBSession = Annotated[Session, Depends(get_db)]


Base.metadata.create_all(bind=engine)


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: DBSession):
    posts = [
        PostResponse.model_validate(p) for p in db.execute(select(Post)).scalars().all()
    ]
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )


@app.get("/post/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int, db: DBSession):
    post = db.execute(select(Post).where(Post.id == post_id)).scalar_one_or_none()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    ret_post = PostResponse.model_validate(post)
    title = ret_post.title[:50]
    return templates.TemplateResponse(
        request,
        "post.html",
        {"post": ret_post, "title": title},
    )


@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: DBSession):
    posts = db.execute(select(Post)).scalars().all()
    return [PostResponse.model_validate(p) for p in posts]


@app.get("/api/post/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: DBSession):
    post = db.execute(select(Post).where(Post.id == post_id)).scalar_one_or_none()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return PostResponse.model_validate(post)


@app.post("/api/post", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: DBSession):
    new_post = Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    return {
        "message": "New post created",
        "post:": PostResponse.model_validate(new_post),
    }


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = (
        exc.detail or "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": message},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exc.status_code,
            "title": exc.status_code,
            "message": message,
        },
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exc.errors()},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
