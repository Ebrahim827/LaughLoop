from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func

from app.database.database import Base


class UserInteraction(Base):
    __tablename__ = "user_interactions"

    interaction_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.user_id"))

    joke_id = Column(Integer, ForeignKey("jokes.joke_id"))

    rating = Column(Integer)

    liked = Column(Boolean, default=False)

    disliked = Column(Boolean, default=False)

    time_spent = Column(Float, default=0)

    viewed_at = Column(TIMESTAMP, server_default=func.now())