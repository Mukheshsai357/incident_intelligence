import os
from dotenv import load_dotenv
# from google import genai
from groq import Groq

load_dotenv()

# client=genai.Client(
#     api_key=os.getenv("GEMINI_API_KEY")
# )

client=Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# def generate_answer(question:str):
#     response=client.models.generate_content(
#         model="gemini-3.5-flash-lite",
#         contents=question
#     )

#     return response.text


def generate_answer(question:str,retrieved_chunks:list):

    context="\n\n".join(
        chunk.content for chunk in retrieved_chunks
    )

    prompt=f"""
    You are an enterprise IT Support assistant

    Answer the users's question using ONLY theinformation provided in the context.

    If the context does not contain the answer,say that you do not have enough information

    Context:
    {context}

    User Question:
    {question}

    Answer:
            """

    response=client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response.choices[0].message.content


