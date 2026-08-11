import math
from pathlib import Path

import streamlit as st
from openai import OpenAI


EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding(client: OpenAI, text: str):
    """
    Convert text into an embedding vector.
    """

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def cosine_similarity(vector_a, vector_b):
    """
    Compare two embedding vectors.

    Higher scores mean the vectors are more similar.
    """

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (
        magnitude_a * magnitude_b
    )


@st.cache_data(show_spinner=False)
def load_knowledge_documents():
    """
    Load knowledge-base Markdown documents from disk.

    Streamlit caches the result so the files are not
    repeatedly read during normal app reruns.
    """

    kb_path = Path("knowledge_base")

    documents = []

    for file in kb_path.glob("*.md"):

        with open(
            file,
            "r",
            encoding="utf-8",
        ) as f:

            content = f.read()

        documents.append(
            {
                "filename": file.name,
                "content": content,
            }
        )

    return documents


def build_document_embeddings(client: OpenAI):
    """
    Create embeddings for all knowledge-base documents.

    Document embeddings are stored in Streamlit session state
    so they do not need to be regenerated for every question.
    """

    if "document_embeddings" in st.session_state:
        return st.session_state.document_embeddings

    documents = load_knowledge_documents()

    embedded_documents = []

    for document in documents:

        document_text = (
            f"Document: {document['filename']}\n\n"
            f"{document['content']}"
        )

        embedding = get_embedding(
            client,
            document_text,
        )

        embedded_documents.append(
            {
                "filename": document["filename"],
                "content": document["content"],
                "embedding": embedding,
            }
        )

    st.session_state.document_embeddings = embedded_documents

    return embedded_documents


def semantic_search_knowledge_base(
    client: OpenAI,
    query: str,
    top_k: int = 3,
):
    """
    Search knowledge-base documents using semantic similarity.
    """

    query_embedding = get_embedding(
        client,
        query,
    )

    documents = build_document_embeddings(
        client
    )

    results = []

    for document in documents:

        score = cosine_similarity(
            query_embedding,
            document["embedding"],
        )

        results.append(
            (
                score,
                document["filename"],
                document["content"],
            )
        )

    results.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return results[:top_k]