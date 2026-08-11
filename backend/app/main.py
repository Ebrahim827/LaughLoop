from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.include_router(auth_router, prefix="/api")
app.include_router(jokes_router, prefix="/api")
app.include_router(interactions_router, prefix="/api")
app.include_router(recommendation_router, prefix="/api")
app.include_router(explanation_router, prefix="/api")
app.include_router(preferences_router, prefix="/api")

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