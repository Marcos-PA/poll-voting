from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Vote(Base):
    __tablename__ = "votes"
    # One vote per voter per poll, enforced by the database. This also covers two concurrent
    # requests, which an app-level "already voted?" check would let through.
    __table_args__ = (UniqueConstraint("poll_id", "voter_id", name="uq_votes_poll_voter"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    poll_id: Mapped[int] = mapped_column(ForeignKey("polls.id"))
    option_id: Mapped[int] = mapped_column(ForeignKey("poll_options.id"), index=True)
    voter_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
