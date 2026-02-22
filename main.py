from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# { Start fake data section
from faker import Faker  # noqa: E402

f = Faker()


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


@app.get("/posts", response_class=HTMLResponse, include_in_schema=False)
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    rdata = "<h1>Home Page</h1>"
    rdata += "<ul>"
    for post in posts:
        rdata += f"<li>{post['id']} {post['author']} {post['title']} {post['date_posted']}</li>"
    rdata += "</ul>"
    return rdata


@app.get("/api/posts")
def get_posts() -> list[dict[str, int | str]]:
    return posts
