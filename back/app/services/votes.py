from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.poll import PollOption
from app.models.vote import Vote
from app.schemas.vote import VoteCreate
from app.services.polls import get_poll


def create_vote(db: Session, poll_id: int, data: VoteCreate) -> Vote:
    get_poll(db, poll_id)
    option = db.get(PollOption, data.option_id)
    if option is None:
        raise HTTPException(status_code=404, detail="Option not found")
    if option.poll_id != poll_id:
        raise HTTPException(status_code=422, detail="Option does not belong to this poll")

    # No "already voted?" pre-check: it would race. The unique constraint (poll_id, voter_id)
    # decides, for both a repeated vote and two concurrent ones.
    vote = Vote(poll_id=poll_id, option_id=option.id, voter_id=data.voter_id)
    db.add(vote)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You have already voted on this poll") from None
    db.refresh(vote)
    return vote
