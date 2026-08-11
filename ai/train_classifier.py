import os
from pathlib import Path

import joblib
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine

from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

# ==========================
# Load .env
# ==========================

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ==========================
# Database
# ==========================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print(f"Connected to {DB_NAME}")

# ==========================
# Load labelled jokes
# ==========================

query = """
SELECT
    j.joke_id,
    CONCAT(j.question,' ',j.answer) AS joke_text,
    c.category_name
FROM jokes j
JOIN joke_categories jc
ON j.joke_id = jc.joke_id
JOIN categories c
ON jc.category_id = c.category_id
ORDER BY j.joke_id;
"""

df = pd.read_sql(query, engine)

dataset = (
    df.groupby(["joke_id","joke_text"])["category_name"]
      .apply(list)
      .reset_index()
)

print("\nTotal labelled jokes:", len(dataset))

# ==========================
# Features
# ==========================

X = dataset["joke_text"]

mlb = MultiLabelBinarizer()

Y = mlb.fit_transform(dataset["category_name"])

print("\nCategories Learned:")

for c in mlb.classes_:
    print("-", c)

# ==========================
# TF-IDF
# ==========================

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    max_features=10000,
    ngram_range=(1,2)
)

X_vector = vectorizer.fit_transform(X)

print("\nVocabulary Size:", len(vectorizer.vocabulary_))

# ==========================
# Train Test Split
# ==========================

X_train, X_test, Y_train, Y_test = train_test_split(
    X_vector,
    Y,
    test_size=0.20,
    random_state=42
)

print("\nTraining:", X_train.shape[0])
print("Testing :", X_test.shape[0])

# ==========================
# Train Model
# ==========================

print("\nTraining model...\n")

model = OneVsRestClassifier(
    LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    )
)

model.fit(
    X_train,
    Y_train
)

print("Training Complete!")

# ==========================
# Evaluate
# ==========================

predictions = model.predict(X_test)

print("\nClassification Report:\n")

print(
    classification_report(
        Y_test,
        predictions,
        target_names=mlb.classes_,
        zero_division=0
    )
)

# ==========================
# Save Files
# ==========================

MODEL_DIR = Path(__file__).resolve().parent

joblib.dump(model, MODEL_DIR / "model.pkl")
joblib.dump(vectorizer, MODEL_DIR / "vectorizer.pkl")
joblib.dump(mlb, MODEL_DIR / "mlb.pkl")

print("\n==============================")
print("MODEL TRAINED SUCCESSFULLY")
print("==============================")

print("Saved:")
print("model.pkl")
print("vectorizer.pkl")
print("mlb.pkl")