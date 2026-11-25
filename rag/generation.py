import os
from dotenv import load_dotenv
# from google import genai
from groq import Groq
from functools import lru_cache

load_dotenv()

# client=genai.Client(
#     api_key=os.getenv("GEMINI_API_KEY")
# )

def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))



# def generate_answer(question:str):
#     response=client.models.generate_content(
#         model="gemini-3.5-flash-lite",
#         contents=question
#     )

#     return response.text


def generate_answer(question:str,retrieved_chunks:list,history:list=None):

    context="\n\n".join(
        chunk.content for chunk in retrieved_chunks
    )

    messages=[
        {
            "role":"system",
            "content":f"""
                    You are an enterprise IT support assistant.

                    Answer using ONLY the provided context.
                    If the context is insufficient, say so.

                    Context:
                    {context}
                    """
        }
    ]

    for msg in history or []:
        messages.append({
            "role":msg.role,
            "content":msg.message
        })
    messages.append({
        "role":"user",
        "content":question
    })

    response=get_groq_client().chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages
    )

    return response.choices[0].message.content


