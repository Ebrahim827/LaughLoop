from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.models.interaction import UserInteraction
from app.models.joke import Joke

router = APIRouter()


@router.get("/preferences/{user_id}")
def preferences(user_id: int, db: Session = Depends(get_db)):

    rows = (
        db.query(
            Joke.ai_category,
            func.count(UserInteraction.interaction_id)
        )
        .join(
            UserInteraction,
            Joke.joke_id == UserInteraction.joke_id
        )
        .filter(
            UserInteraction.user_id == user_id,
            UserInteraction.liked == True
        )
        .group_by(Joke.ai_category)
        .all()
    )

    return [
        {
            "category": row[0],
            "count": row[1]
        }
        for row in rows
    ]