# app/llm.py
import os
from dotenv import load_dotenv

load_dotenv()

# support both new OpenAI SDK and legacy `openai` package
try:
    from openai import OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=OPENAI_API_KEY)
    _use_new_client = True
except Exception:
    import openai
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set")
    openai.api_key = OPENAI_API_KEY
    _use_new_client = False

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


def generate_answer(context_chunks, question):
    """
    Better prompt:
    - If context contains partial info, model must answer using it.
    - Only say "The document does not contain this information."
      when NOTHING relevant exists.
    """

    context_text = "\n\n---\n\n".join(context_chunks)

    prompt = f"""
You are an expert assistant. Use the following context to answer the question.
If the answer is partially present, answer using what is available.
If you cannot find a direct answer, explain based on the best possible context match.

Context:
{context_text}

Question: {question}

Answer:
"""


    if _use_new_client:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    else:
        response = openai.ChatCompletion.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0
        )
        return response.choices[0].message.content.strip()
