from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.jokes import router as jokes_router
from app.routes.interactions import router as interactions_router
from app.routes.recommendations import router as recommendation_router
from app.routes.explanation import router as explanation_router
from app.routes.preferences import router as preferences_router

app = FastAPI(
    title="HumourAI API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(jokes_router)
app.include_router(interactions_router)
app.include_router(recommendation_router)
app.include_router(explanation_router)
app.include_router(preferences_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to HumourAI!"
    }