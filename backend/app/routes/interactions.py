from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.interaction import UserInteraction
from app.models.joke import Joke
from app.schemas.interaction import InteractionCreate

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"]
)


@router.post("/")
def save_interaction(
    interaction: InteractionCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    new_interaction = UserInteraction(
        user_id=current_user["user_id"],
        joke_id=interaction.joke_id,
        rating=interaction.rating,
        liked=interaction.liked,
        disliked=interaction.disliked,
        time_spent=interaction.time_spent
    )

    db.add(new_interaction)
    db.commit()

    return {"message": "Interaction saved successfully!"}


@router.get("/saved")
def get_saved_jokes(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    saved = (
        db.query(Joke)
        .join(UserInteraction, Joke.joke_id == UserInteraction.joke_id)
        .filter(
            UserInteraction.user_id == current_user["user_id"],
            UserInteraction.liked == True
        )
        .order_by(UserInteraction.interaction_id.desc())
        .all()
    )

    return saved

@router.delete("/saved/{joke_id}")
def remove_saved(
    joke_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    interaction = (
        db.query(UserInteraction)
        .filter(
            UserInteraction.user_id == current_user["user_id"],
            UserInteraction.joke_id == joke_id,
            UserInteraction.liked == True
        )
        .first()
    )

    if interaction:
        db.delete(interaction)
        db.commit()

    return {"message": "Removed"}    