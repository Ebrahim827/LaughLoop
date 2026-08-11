import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY not found.")

print(f"Connected to database: {DB_NAME}")

client = genai.Client(api_key=GEMINI_API_KEY)

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# ==========================
# Categories
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

CATEGORY_LIST = list(CATEGORY_MAP.keys())


# ==========================
# Load uncategorized jokes
# ==========================

def get_uncategorized_jokes(limit=100):

    sql = text("""
        SELECT joke_id, question, answer
        FROM jokes
        WHERE joke_id NOT IN (
            SELECT joke_id
            FROM joke_categories
        )
        ORDER BY joke_id
        LIMIT :limit
    """)

    with engine.connect() as conn:
        return conn.execute(sql, {"limit": limit}).fetchall()


# ==========================
# Gemini Classification
# ==========================

def classify_joke(question, answer):

    prompt = f"""
You are a joke classifier.

Choose ONLY categories from this list.

{", ".join(CATEGORY_LIST)}

Rules:

Return ONLY category names.

Maximum 3 categories.

Comma separated.

No explanations.

Question:
{question}

Answer:
{answer}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    categories = []

    for item in response.text.split(","):

        item = item.strip()

        if item in CATEGORY_MAP:
            categories.append(item)

    return list(set(categories))


# ==========================
# Save categories
# ==========================

def save_categories(joke_id, categories):

    if not categories:
        return

    sql = text("""
        INSERT IGNORE INTO joke_categories
        (joke_id, category_id)
        VALUES
        (:joke_id,:category_id)
    """)

    with engine.begin() as conn:

        for category in categories:

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

    BATCH_SIZE = 100

    while True:

        jokes = get_uncategorized_jokes(BATCH_SIZE)

        if not jokes:
            print("\n===================================")
            print("ALL JOKES HAVE BEEN CATEGORIZED!")
            print("===================================")
            break

        print(f"\nLoaded {len(jokes)} jokes...\n")

        for index, joke in enumerate(jokes, start=1):

            print("-" * 60)
            print(f"[{index}/{len(jokes)}]")
            print(f"Joke ID : {joke.joke_id}")

            try:

                categories = classify_joke(
                    joke.question,
                    joke.answer
                )

                if categories:

                    save_categories(
                        joke.joke_id,
                        categories
                    )

                    print("Saved:", ", ".join(categories))

                else:

                    print("Gemini returned no valid category.")

            except Exception as e:

               print("ERROR:", e)

               if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("Rate limit reached. Waiting 65 seconds...")
               time.sleep(65)
            else:
               time.sleep(5)

               continue

            # small delay to avoid API rate limits
            time.sleep(1)

        print("\nBatch Finished.\n")            