

from langchain_huggingface import HuggingFaceEmbeddings

from config import HUGGINGFACE_CONFIG

model_name = HUGGINGFACE_CONFIG['embedding_model']
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": False}
hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)

def generate_embedding(text) ->str:
    """
    Generate an embedding for the given text using the specified model.

    Args:
        text (str): The input text to generate an embedding for.

    Returns:
        np.ndarray: The generated embedding as a NumPy array.
    """

   
    embedding = hf.embed_query(text)
    # embedding = ollama.embeddings(
    #     model=OLLAMA_CONFIG['model'], prompt=text
    # ).embedding
    # Convert to PostgreSQL vector format
    return turn_vector_to_str(embedding)


def turn_vector_to_str(vector):
    """
    Convert a vector (list or np.ndarray) to a string format suitable for PostgreSQL vector type.

    Args:
        vector (list or np.ndarray): The input vector.

    Returns:
        str: The vector as a string formatted for PostgreSQL.
    """
    return '[' + ','.join(map(str, vector)) + ']'
