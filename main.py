from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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


@app.get("/api/posts")
def get_posts() -> list[dict[str, int | str]]:
    return posts
