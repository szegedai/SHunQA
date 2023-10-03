import time
from fastapi import APIRouter, HTTPException
import logging

from backend.model_types import InputModel, OutputModel, ErrorModel
from backend.exceptions import CheckFailError, PipelineFailError
from backend.settings import pipeline, pipeline_end
from backend.settings.environment import mongo_client, environment

logger = logging.getLogger(__name__)

route = APIRouter()


@route.get("")
async def question(input: InputModel):
    """This endpoint is used to ask a question.

    Args:
        input (InputModel): Give the question you want to ask.

    Raises:
        HTTPException: If something goes wrong.

    Returns:
        OutputModel: The answer to your question.
    """
    try:
        data = pipeline.run({"query": input.query})
        data = pipeline_end.run(data)
        return OutputModel(
            answer=data["reader"]["answer"],
            context=data["context"],
            text_start=data["reader"]["start"],
            text_end=data["reader"]["end"],
            metadata=data["metadata"],
            id=data["id"],
            debug=data if environment.debug else None,
            elastic_score=data["scores"] if environment.debug else None,
            reader_score=data["reader"]["score"] if environment.debug else None,
        )
    except CheckFailError as e:
        logger.error(e)
        data = pipeline_end.run(e.data)
        mongo_client["shunqa"]["errors"].insert_one(
            {
                "error": e.error_code,
                "time": time.time(),
                "type": "check_in_question",
                "id": data["id"],
            }
        )
        raise HTTPException(
            status_code=400,
            detail=ErrorModel(error=e.error_code, id=data["id"]).model_dump(),
        )
    except PipelineFailError as e:
        logger.error(e)
        data = pipeline_end.run(e.data)
        mongo_client["shunqa"]["errors"].insert_one(
            {
                "error": e.error_code,
                "time": time.time(),
                "type": "pipeline_in_question",
                "id": data["id"],
            }
        )
        raise HTTPException(
            status_code=400,
            detail=ErrorModel(error=e.error_code, id=data["id"]).model_dump(),
        )
    except Exception as e:
        logger.error(e)
        mongo_client["shunqa"]["errors"].insert_one(
            {
                "error": str(e),
                "time": time.time(),
                "type": "unknown_error_in_question",
                "input_query": input.model_dump(),
            }
        )
        raise HTTPException(
            status_code=400, detail=ErrorModel(error="unknown_error").model_dump()
        )
