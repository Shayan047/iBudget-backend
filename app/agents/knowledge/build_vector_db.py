from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import shutil
import os

KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), "ibudget_knowledge.md")
VECTOR_DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")


def build_vector_db():

    if os.path.exists(VECTOR_DB_PATH):
        shutil.rmtree(VECTOR_DB_PATH)
        print("Existing vector DB cleared.")

    # Step 1 — Load the document
    loader = TextLoader(KNOWLEDGE_PATH)
    documents = loader.load()

    # Step 2 — Split by markdown headers so each section is a chunk
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
    )
    chunks = splitter.split_text(documents[0].page_content)

    # Step 3 — Create embeddings model (runs locally, free)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Step 4 — Store chunks + their embeddings in ChromaDB
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_PATH,
    )

    print(f"Vector DB built with {len(chunks)} chunks")
    return vector_db


if __name__ == "__main__":
    build_vector_db()
