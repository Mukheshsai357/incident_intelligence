from rag.generation import get_groq_client

def rewrite_question(question:str,history:list=None):
    if not history:
        return question

    messages=[
        {
            "role": "system",
            "content":""" 
                    You are a query rewriting assistant. 

                    Your task is to rewrite the user's latest question into a standalone question using the conversation history. 

                    Rules:
                    - Resolve references such as it,that,this, and they. 
                    - Preserve the original meaning. 
                    - Do not answer the question. 
                    - Do not add information that is not in the conversation. 
                    - Return only the rewritten question. 
                    """
        }
    ]

    for msg in history:
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

    return response.choices[0].message.content.strip()