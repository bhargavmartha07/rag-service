# app/llm.py
import os
from dotenv import load_dotenv

load_dotenv()

# prefer new OpenAI SDK if installed; fallback to openai package
try:
    from openai import OpenAI
    _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    _use_new = True
except Exception:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    _use_new = False

def generate_answer(context_chunks, question):
    """
    Build a prompt and call the LLM. Returns text answer.
    """
    if not context_chunks:
        return "No context available to answer the question."

    context_text = "\n\n".join(context_chunks)
    prompt = f"""You are a helpful assistant. Use the context below to answer the user's question.
If the answer is not present in the context, say "The document does not contain this information."

Context:
{context_text}

Question: {question}
Answer:"""

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        return "OpenAI API key not configured on server."

    try:
        if _use_new:
            # New OpenAI client style
            response = _client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            # Some clients return choices differently
            return response.choices[0].message.content
        else:
            # Legacy openai package
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            return resp["choices"][0]["message"]["content"]
    except Exception as e:
        print("LLM call failed:", e)
        return "LLM call failed: " + str(e)
