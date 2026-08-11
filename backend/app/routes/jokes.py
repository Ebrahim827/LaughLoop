from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from app.database.database import get_db
from app.models.joke import Joke
from app.schemas.joke import JokeResponse

router = APIRouter(prefix="/jokes", tags=["Jokes"])


@router.get("/random", response_model=JokeResponse)
def random_joke(db: Session = Depends(get_db)):

    joke = db.query(Joke).order_by(func.rand()).first()

    return joke