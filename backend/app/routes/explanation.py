from fastapi import APIRouter
from pydantic import BaseModel
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter()

class Joke(BaseModel):
    question:str
    answer:str

@router.post("/explain")
def explain(joke:Joke):

    prompt=f"""
Explain this joke in 2-4 simple sentences.

Question:
{joke.question}

Answer:
{joke.answer}

Explain the humour without repeating the joke.
"""

    response=client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return{
        "explanation":response.text
    }