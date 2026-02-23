from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import PostCreate, PostResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), "static")

# { Start fake data section
from faker import Faker  # noqa: E402

f = Faker()
templates = Jinja2Templates(directory="templates")


def gen_rand_post(id: int) -> dict[str, str | int]:
    return {
        "id": id,
        "author": f"{f.name()} {f.last_name()}",
        "title": f.text(30),
        "content": f.text(100),
        "date_posted": f.date(),
    }


posts: list[dict] = [
    gen_rand_post(1),
    gen_rand_post(2),
    gen_rand_post(3),
]

# } End fake data section


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(
        request, "home.html", {"posts": posts, "title": "Home"}
    )


@app.get("/post/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int):
    for post in posts:
        if post["id"] == post_id:
            title = post["title"][:50]
            return templates.TemplateResponse(
                request, "post.html", {"post": post, "title": title}
            )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts


@app.get("/api/post/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Post not found")


@app.post("/api/post", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    post_ = {
        **post.model_dump(),
        "id": max([p["id"] for p in posts]) + 1 if posts else 1,
        "date_posted": datetime.now().strftime("%F %T"),
    }
    posts.append(post_)
    return {"message": "New post created", "post:": post_}


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
