import time
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from backend.types import FeedbackLikeModel, FeedbackDislikeModel, ErrorModel
from backend.settings.environment import mongo_client

route = APIRouter()


@route.post("/like")
def like(input: FeedbackLikeModel):
    """This endpoint is used to like a question.

    Args:
        input (FeedbackLikeModel): Give the id of the question you want to like.

    Raises:
        HTTPException: If something goes wrong.

    Returns:
        Response: HTTP 200 if everything went well.
    """
    try:
        input.time = time.time()
        mongo_client["shunqa"]["likes"].insert_one(input.model_dump().copy())
        return Response(status_code=200)
    except Exception as e:
        mongo_client["shunqa"]["errors"].insert_one(
            {"error": str(e), "time": time.time(), "type": "like"}
        )
        raise HTTPException(
            status_code=400, detail=ErrorModel(error="unknown_error").model_dump()
        )


@route.post("/dislike")
def dislike(input: FeedbackDislikeModel):
    """This endpoint is used to dislike a question.

    Args:
        input (FeedbackDislikeModel): Give the id and other feedback parameters of the question you want to dislike.

    Raises:
        HTTPException: If something goes wrong.

    Returns:
        Response: HTTP 200 if everything went well.
    """
    try:
        input.time = time.time()
        mongo_client["shunqa"]["dislikes"].insert_one(input.model_dump().copy())
        return Response(status_code=200)
    except Exception as e:
        mongo_client["shunqa"]["errors"].insert_one(
            {"error": str(e), "time": time.time(), "type": "dislike"}
        )
        raise HTTPException(
            status_code=400, detail=ErrorModel(error="unknown_error").model_dump()
        )
