from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.poll import PollOption
from app.models.vote import Vote
from app.schemas.result import OptionResult, PollResults
from app.services.polls import get_poll


def get_results(db: Session, poll_id: int, voter_id: str | None) -> PollResults:
    poll = get_poll(db, poll_id)

    # Counting happens in the database: one GROUP BY. The outer join keeps options with no votes
    # (count of NULL = 0).
    rows = db.execute(
        select(PollOption.id, PollOption.text, func.count(Vote.id))
        .outerjoin(Vote, Vote.option_id == PollOption.id)
        .where(PollOption.poll_id == poll_id)
        .group_by(PollOption.id, PollOption.text)
        .order_by(PollOption.id)
    ).all()
    total = sum(votes for _, _, votes in rows)

    voted_option_id = None
    if voter_id:
        voted_option_id = db.scalar(
            select(Vote.option_id).where(Vote.poll_id == poll_id, Vote.voter_id == voter_id)
        )

    return PollResults(
        poll_id=poll.id,
        question=poll.question,
        total_votes=total,
        voted_option_id=voted_option_id,
        options=[
            OptionResult(
                id=id_,
                text=text,
                votes=votes,
                percentage=round(votes * 100 / total, 1) if total else 0.0,
            )
            for id_, text, votes in rows
        ],
    )
