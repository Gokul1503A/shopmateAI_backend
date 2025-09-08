from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Initialize the embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# In-memory knowledge base
kb = []
kb_embeddings = []

def add_to_kb(text: str):
    """
    Add a text entry to the knowledge base and store its embedding.
    """
    kb.append(text)
    embedding = embedding_model.encode([text])[0]
    kb_embeddings.append(embedding)

def retrieve_similar(query: str, top_k=3):
    """
    Retrieve top_k similar entries from the knowledge base given a query.
    Returns a list of tuples (text, similarity_score).
    """
    if not kb:
        return []
    query_embedding = embedding_model.encode([query])[0].reshape(1, -1)
    embeddings_matrix = np.array(kb_embeddings)
    similarities = cosine_similarity(query_embedding, embeddings_matrix)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    results = [(kb[i], similarities[i]) for i in top_indices]
    return results
