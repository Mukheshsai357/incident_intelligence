from rag.retrieval import search_similar_chunks
from rag.generation import generate_answer

def run_rag_pipeline(question:str): 
    
    retrieved_chunks=search_similar_chunks(
        question,
        top_k=3
    )

    #apply similarity  threshold

    relevant_chunks=[
        chunk for chunk in retrieved_chunks
        if chunk.distance<=0.5
    ]

    if not relevant_chunks:
        return "I don't have enough information to answer this question."

    answer=generate_answer(
        question,relevant_chunks
    )


    

    return answer

if __name__=="__main__":
    question = "Why is my VPN not connecting?"
    answer=run_rag_pipeline(question)

    print("\n Answer: ")
    print(answer)