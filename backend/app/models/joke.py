from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    Enum,
    Boolean,
    TIMESTAMP,
    ForeignKey,
)

from app.database.database import Base


class Joke(Base):
    __tablename__ = "jokes"

    joke_id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.category_id")
    )

    ai_category = Column(String(100))

    difficulty = Column(
        Enum("Easy", "Medium", "Hard")
    )

    language = Column(String(30))

    is_active = Column(Boolean)

    created_at = Column(TIMESTAMP)