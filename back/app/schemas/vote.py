from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints


class VoteCreate(BaseModel):
    option_id: int
    voter_id: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]


class VoteResponse(BaseModel):
    id: int
    poll_id: int
    option_id: int
    created_at: datetime
    model_config = {"from_attributes": True}
