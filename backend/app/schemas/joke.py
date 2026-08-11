from pydantic import BaseModel


class JokeResponse(BaseModel):
    joke_id: int
    question: str
    answer: str

    class Config:
        from_attributes = True