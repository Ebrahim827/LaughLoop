import os
from pathlib import Path

import joblib

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ==========================
# Load .env
# ==========================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# ==========================
# Environment Variables
# ==========================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

print(f"Connected to {DB_NAME}")


# ==========================
# Database
# ==========================

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# ==========================
# Load ML Files
# ==========================

MODEL_DIR = Path(__file__).resolve().parent

model = joblib.load(MODEL_DIR / "model.pkl")
vectorizer = joblib.load(MODEL_DIR / "vectorizer.pkl")
mlb = joblib.load(MODEL_DIR / "mlb.pkl")

print("Model Loaded Successfully")


# ==========================
# Category IDs
# ==========================

CATEGORY_MAP = {
    "Dad Jokes": 1,
    "Programming & Tech": 2,
    "Animals": 3,
    "School & Education": 4,
    "Science & Math": 5,
    "Medical & Health": 6,
    "Food & Drinks": 7,
    "Work & Office": 8,
    "Relationships & Family": 9,
    "Dark Humour": 10,
    "Puns & Wordplay": 11,
    "Politics": 12,
    "Sports": 13,
    "Military": 14,
    "Miscellaneous": 15,
}


# ==========================
# Load Remaining Jokes
# ==========================

def get_remaining_jokes(limit=500):

    sql = text("""
        SELECT
            joke_id,
            question,
            answer
        FROM jokes
        WHERE joke_id NOT IN (
            SELECT joke_id
            FROM joke_categories
        )
        ORDER BY joke_id
        LIMIT :limit
    """)

    with engine.connect() as conn:
        return conn.execute(
            sql,
            {"limit": limit}
        ).fetchall()


# ==========================
# Predict Categories
# ==========================

def predict_categories(question, answer):

    joke = f"{question} {answer}"

    X = vectorizer.transform([joke])

    probabilities = model.predict_proba(X)[0]

    scores = []

    # Apply penalties
    for category, probability in zip(mlb.classes_, probabilities):

        if category == "Miscellaneous":
            probability -= 0.20

        if category == "Dark Humour":
            probability -= 0.08

        if category == "Animals":
            probability -= 0.05

        if category == "Puns & Wordplay":
            probability -= 0.13        

        scores.append((category, probability))

    # Keyword boosts
    text = joke.lower()

    for i, (category, probability) in enumerate(scores):

        if category == "Sports":
            if any(word in text for word in [
                "football", "soccer", "basketball", "baseball",
                "tennis", "golf", "cricket", "olympic",
                "olympics", "sport", "race", "player",
                "coach", "stadium", "game", "goal",
                "league", "champion", "medal", "athlete",
                "frisbee", "discus"
            ]):
                scores[i] = (category, probability + 0.25)

        elif category == "Science & Math":
            if any(word in text for word in [
                "math", "mathematics", "equation", "physics",
                "chemist", "chemistry", "acid", "molecule",
                "science", "scientist", "formula", "number",
                "plus", "minus", "calculate", "algebra", "geometry", "calculus"
            ]):
                scores[i] = (category, probability + 0.25)

        elif category == "Military":
            if any(word in text for word in [
                "army", "soldier", "tank", "war", "gun",
                "missile", "navy", "marine", "general",
                "captain", "battle", "bomb"
            ]):
                scores[i] = (category, probability + 0.30)

        elif category == "Programming & Tech":
            if any(word in text for word in [

                "computer", "pc", "laptop",
                "internet", "wifi", "web", "website",
                "software", "hardware",
                "program", "programming", "programmer",
                "code", "coding", "bug", "debug",
                "python", "java", "javascript",
                "c++", "c#", "html", "css",
                "sql", "mysql", "database", "api",
                "server", "cloud",
                "google", "reddit", "youtube",
                "facebook", "instagram", "twitter",
                "android", "iphone", "ios", "samsung",
                "robot", "ai", "chatgpt", "gemini",
                "linux", "windows"

            ]):
                scores[i] = (category, probability + 0.25)        

    # Sort predictions
    scores.sort(key=lambda x: x[1], reverse=True)

    predictions = []

    # Always keep best prediction
    predictions.append(scores[0][0])

    # Keep second if close
    if scores[1][1] >= scores[0][1] * 0.80:
        predictions.append(scores[1][0])

    # Keep third if close
    if scores[2][1] >= scores[0][1] * 0.70:
        predictions.append(scores[2][0])

    return predictions


# ==========================
# Save Predictions
# ==========================

def save_categories(joke_id, categories):

    if not categories:
        return

    sql = text("""
        INSERT IGNORE INTO joke_categories
        (joke_id, category_id)
        VALUES
        (:joke_id, :category_id)
    """)

    with engine.begin() as conn:

        for category in categories:

            if category not in CATEGORY_MAP:
                continue

            conn.execute(
                sql,
                {
                    "joke_id": joke_id,
                    "category_id": CATEGORY_MAP[category]
                }
            )


# ==========================
# Main
# ==========================

if __name__ == "__main__":

    BATCH_SIZE = 36000
    total_processed = 0

    jokes = get_remaining_jokes(BATCH_SIZE)

    if not jokes:
        print("\n===================================")
        print("ALL JOKES HAVE BEEN CATEGORIZED!")
        print("===================================")
        exit()

    print(f"\nLoaded {len(jokes)} remaining jokes...\n")

    for index, joke in enumerate(jokes, start=1):

        print("-" * 60)
        print(f"[{index}/{len(jokes)}]")
        print(f"Joke ID : {joke.joke_id}")

        categories = predict_categories(
            joke.question,
            joke.answer
        )

        if categories:

            save_categories(
                joke.joke_id,
                categories
            )

            print("Predicted:", ", ".join(categories))

        else:

            print("No category predicted.")

        total_processed += 1

    print("\n===================================")
    print("TEST BATCH FINISHED")
    print("===================================")
    print("Total Processed:", total_processed)