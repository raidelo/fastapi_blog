import uvicorn


def main() -> None:
    uvicorn.run("fastapi_blog.main:app", reload=True)


if __name__ == "__main__":
    main()
