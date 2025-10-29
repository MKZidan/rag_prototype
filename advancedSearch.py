


import time
from transformers import pipeline

from config import OPENROUTER_CONFIG, SEARCH_CONFIG
from database import SearchDB
from embedding_generator import generate_embedding
import embedding_generator
from openai import OpenAI

client = OpenAI(
    base_url=OPENROUTER_CONFIG['base_url'],
    api_key=OPENROUTER_CONFIG['api_key'],
)

def get_answer(prompt):
    completion = client.chat.completions.create(
    extra_body={},
    model=OPENROUTER_CONFIG['chat_model'],
    messages=[
        {
        "role": "user",
        "content": prompt
        }
    ]
    )
    answer = completion.choices[0].message.content
    return answer

if __name__ == "__main__":
    # Example usage
    import argparse

    parser = argparse.ArgumentParser(description="Search the knowledge base")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=SEARCH_CONFIG['default_count'], help="Number of results")
    parser.add_argument("--threshold", type=float, default=SEARCH_CONFIG['default_threshold'], help="Similarity threshold")
    args = parser.parse_args()

    # parser.add_argument("--doc-id", type=int, help="Search within specific document")
    PROMPT_TEMPLATE_0 = """
        You are a helpful research assistant. 
        Provide an example answer to the given question, that might be found in a news article, document or report.

        Answer the question in less than 150 words based on the above context in one paragraph: {query}
        """
    PROMPT_TEMPLATE_1 = """
    Answer the question based only on the following context:

    {context}

    Answer the question based on the above context: {query}
    If the question can't be answered based on the context, say "I don't know."
    """    
    # response = ollama.generate(
    #     model="llama3.1",
    #     prompt=PROMPT_TEMPLATE_0.format(query=args.query)
    # )
    response = get_answer(PROMPT_TEMPLATE_0.format(query=args.query))
    # print("Generated preliminary answer:", response)
    query = args.query + " " + response
    embeddings = generate_embedding(query)
    db = SearchDB()
    start_search_time = time.time()
    results = db.search_similar_chunks(embeddings, args.threshold, args.limit)

    end_search_time = time.time()
    print(f"Search time: {end_search_time - start_search_time:.2f} seconds")
    context = ""
    
    for result in results:
        context += result[1] + "\n"

    response = get_answer(PROMPT_TEMPLATE_1.format(context=context, query=args.query))

    print("\nFinal Answer:\n", response)