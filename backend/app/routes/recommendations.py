from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import random

from app.database.database import get_db
from app.models.interaction import UserInteraction
from app.models.joke import Joke

router = APIRouter()


@router.get("/recommendations/{user_id}")
def recommend(
    user_id: int,
    db: Session = Depends(get_db)
):

    # ==========================
    # User's liked categories
    # ==========================

    top_categories = (
        db.query(
            Joke.ai_category,
            func.count(
                UserInteraction.interaction_id
            ).label("likes")
        )
        .join(
            UserInteraction,
            Joke.joke_id == UserInteraction.joke_id
        )
        .filter(
            UserInteraction.user_id == user_id,
            UserInteraction.liked == True
        )
        .group_by(
            Joke.ai_category
        )
        .order_by(
            func.count(
                UserInteraction.interaction_id
            ).desc()
        )
        .all()
    )

    # ==========================
    # New user
    # ==========================

    if len(top_categories) == 0:

        joke = (
            db.query(Joke)
            .filter(Joke.is_active == True)
            .order_by(func.rand())
            .first()
        )

        return joke

    # ==========================
    # Recommendation Strategy
    # ==========================

    r = random.random()

    # 40% favourite category
    if r < 0.40:

        chosen_category = top_categories[0][0]

    # 40% any liked category
    elif r < 0.80:

        chosen_category = random.choice(top_categories)[0]

    # 20% exploration
    else:

        ignored = [
            "Dad Jokes",
            "Puns & Wordplay",
            "Dark Humour"
        ]

        categories = (
            db.query(Joke.ai_category)
            .filter(
                Joke.is_active == True,
                ~Joke.ai_category.in_(ignored)
            )
            .distinct()
            .all()
        )

        chosen_category = random.choice(categories)[0]

    # ==========================
    # Get joke
    # ==========================

    joke = (
        db.query(Joke)
        .filter(
            Joke.ai_category == chosen_category,
            Joke.is_active == True
        )
        .order_by(func.rand())
        .first()
    )

    # ==========================
    # Fallback
    # ==========================

    if joke is None:

        joke = (
            db.query(Joke)
            .filter(Joke.is_active == True)
            .order_by(func.rand())
            .first()
        )

    return joke