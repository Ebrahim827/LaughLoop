import pandas as pd
from sqlalchemy import create_engine

# Connect to MySQL
engine = create_engine(
    "mysql+pymysql://root:root123@127.0.0.1:3306/HumourAI"
)

# Read the CSV
df = pd.read_csv(r"C:\Users\hme96\Downloads\archive\jokes.csv")

# Remove rows with missing Question or Answer
df = df.dropna(subset=["Question", "Answer"])

# Rename columns to match MySQL table
df.rename(columns={
    "ID": "dataset_id",
    "Question": "question",
    "Answer": "answer"
}, inplace=True)

# Keep only the required columns
df = df[["dataset_id", "question", "answer"]]

# Upload to MySQL
df.to_sql(
    "jokes",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=1000
)

print(f"Successfully loaded {len(df)} jokes into MySQL!")