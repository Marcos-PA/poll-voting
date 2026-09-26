from pydantic import BaseModel


class OptionResult(BaseModel):
    id: int
    text: str
    votes: int
    percentage: float


class PollResults(BaseModel):
    poll_id: int
    question: str
    total_votes: int
    voted_option_id: int | None
    options: list[OptionResult]
