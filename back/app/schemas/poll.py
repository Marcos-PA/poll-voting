from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator

OptionText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class PollCreate(BaseModel):
    question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    options: list[OptionText] = Field(min_length=2, max_length=20)

    @field_validator("options")
    @classmethod
    def unique_options(cls, options: list[str]) -> list[str]:
        if len({o.casefold() for o in options}) != len(options):
            raise ValueError("Options must be unique")
        return options


class PollOptionResponse(BaseModel):
    id: int
    text: str
    model_config = {"from_attributes": True}


class PollResponse(BaseModel):
    id: int
    question: str
    created_at: datetime
    options: list[PollOptionResponse]
    model_config = {"from_attributes": True}
