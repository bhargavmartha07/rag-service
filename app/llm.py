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
You are a helpful assistant.

You must answer the question USING THE CONTEXT BELOW.
Even if the context does not contain a direct definition, you must infer from related sentences.

ONLY IF the context contains absolutely no relevant information,
reply exactly with:
"The document does not contain this information."

Context:
{context_text}

Question:
{question}

Provide the most accurate answer using the available context.
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
