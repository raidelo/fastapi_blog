from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, event, func
from sqlalchemy.orm import Mapped, MappedAsDataclass, QueryContext, mapped_column

from .database import Base


class Post(MappedAsDataclass, Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)

    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        init=False,
    )

    def __repr__(self) -> str:
        return f"<Post id={self.id} date_posted={self.date_posted.isoformat()} title={self.title!r} author={self.author!r} content_length={len(self.content)}>"


@event.listens_for(Post, "load")
def convert_date_posted_to_utc(target: Post, _: QueryContext):
    if target.date_posted and target.date_posted.tzinfo is None:
        target.date_posted = target.date_posted.replace(tzinfo=timezone.utc)
