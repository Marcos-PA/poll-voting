from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.poll import Poll, PollOption
from app.schemas.poll import PollCreate


def create_poll(db: Session, data: PollCreate) -> Poll:
    # Poll and options in a single commit: all or nothing.
    poll = Poll(question=data.question, options=[PollOption(text=t) for t in data.options])
    db.add(poll)
    db.commit()
    db.refresh(poll)
    return poll


def list_polls(db: Session) -> list[Poll]:
    stmt = select(Poll).options(selectinload(Poll.options)).order_by(Poll.id.desc())
    return list(db.scalars(stmt))


def get_poll(db: Session, poll_id: int) -> Poll:
    poll = db.get(Poll, poll_id)
    if poll is None:
        raise HTTPException(status_code=404, detail="Poll not found")
    return poll
