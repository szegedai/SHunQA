from typing import Optional, List
from pydantic import BaseModel


class InputModel(BaseModel):
    query: str


class OutputModel(BaseModel):
    answer: str
    context: str
    text_start: int
    text_end: int
    metadata: list
    id: str
    debug: Optional[dict] = None
    elastic_score: Optional[List[float]] = None
    reader_score: Optional[float] = None


class ErrorModel(BaseModel):
    error: str
    id: Optional[str] = None


class FeedbackDislikeModel(BaseModel):
    id: str
    what_should_be: str
    whats_wrong: str
    anything_else: str
    was_this_in_the_context: str
    time: Optional[float] = None


class FeedbackLikeModel(BaseModel):
    id: str
    time: Optional[float] = None
