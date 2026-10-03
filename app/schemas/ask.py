from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    user_question: str = Field(min_length=1, max_length=500)


class AskResponse(BaseModel):
    source: str
    matched_question: str
    answer: str
