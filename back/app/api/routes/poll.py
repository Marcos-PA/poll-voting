from fastapi import APIRouter

from app.db.session import DbSession
from app.schemas.poll import PollCreate, PollResponse
from app.services import polls as polls_service

router = APIRouter(prefix="/polls", tags=["polls"])


@router.get("", response_model=list[PollResponse])
def list_polls(db: DbSession):
    return polls_service.list_polls(db)


@router.post("", response_model=PollResponse, status_code=201)
def create_poll(db: DbSession, poll: PollCreate):
    return polls_service.create_poll(db, poll)


@router.get("/{poll_id}", response_model=PollResponse)
def get_poll(db: DbSession, poll_id: int):
    return polls_service.get_poll(db, poll_id)
