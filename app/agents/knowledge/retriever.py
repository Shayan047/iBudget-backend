from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")


@lru_cache(maxsize=1)
def get_retriever():
    """
    Load the vector DB once and cache it.
    Returns a retriever that finds relevant chunks for a query.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings,
    )
    # Return top 3 most relevant chunks for any query
    return vector_db.as_retriever(search_kwargs={"k": 3})


def get_relevant_context(query: str) -> str:
    """
    Given a user query, retrieve relevant business knowledge chunks.
    Returns them as a single string to inject into the prompt.
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)
    if not docs:
        return ""
    return "\n\n".join([doc.page_content for doc in docs])
