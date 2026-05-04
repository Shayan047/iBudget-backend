from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")


@lru_cache(maxsize=1)
def get_retriever():
    """
    Loads the vector DB once and cache it.
    Returns the retriever function.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings,
    )

    return vector_db.as_retriever(search_kwargs={"k": 3})


def get_relevant_context(query: str) -> str:
    """
    Based on user query, retrieve relevant business knowledge chunks.
    Returns them as a single string for the prompt.
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)
    if not docs:
        return ""
    return "\n\n".join([doc.page_content for doc in docs])
