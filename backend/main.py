from fastapi import FastAPI

from backend.routes import question_route, feedback_route
from backend.settings import model_settings
from backend.settings.environment import environment


app = FastAPI(docs_url=environment.urls["swagger"], redoc_url=environment.urls["redoc"])

app.include_router(question_route, prefix="/question")
app.include_router(feedback_route, prefix="/feedback")


@app.get("/")
async def root():
    return {"debug": "true" if environment.debug else "false"}
