from pydantic import BaseModel, Field


class InteractionCreate(BaseModel):
    joke_id: int
    rating: int = Field(ge=1, le=5)
    liked: bool = False
    disliked: bool = False
    time_spent: float = 0