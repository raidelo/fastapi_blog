#!/usr/bin/env python

from argparse import ArgumentParser
from datetime import datetime

from faker import Faker
from sqlalchemy import insert, select

from .constants import MAX_TITLE_LENGTH
from .database import SessionMaker
from .models import Post
from .schemas import PostCreate


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("posts_amount", type=int, nargs="?", default=5)

    args = parser.parse_args()

    faker = Faker()

    posts: list[tuple[PostCreate, datetime]] = [
        (
            PostCreate(
                title=faker.text(MAX_TITLE_LENGTH),
                content=faker.text(256),
                author=f"{faker.name()} {faker.last_name()}",
            ),
            faker.date_time_between_dates(
                datetime_start=datetime(year=2000, month=1, day=1),
                datetime_end=datetime.now(),
            ),
        )
        for _ in range(args.posts_amount)
    ]

    with SessionMaker() as db:
        db.execute(
            insert(Post).values(
                [
                    {**post_create.model_dump(), "date_posted": date_posted}
                    for post_create, date_posted in posts
                ]
            )
        )
        db.commit()

        result = db.execute(select(Post)).scalars().all()

        for post in result:
            print("============ NUEVO POST ============")
            print(f"""\
ID         : {post.id}
Title      : {post.title}
Content    : {post.content}
Author     : {post.author}
Date posted: {post.date_posted}""")
            print("====================================\n")

        print(f"Registros insertados en la base de datos: {len(posts)}")
        print(f"Actualmente hay: {len(result)}")


if __name__ == "__main__":
    main()
