import asyncio
import os

from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import pinecone

from src.settings import settings

load_dotenv()

embeddings = OpenAIEmbeddings()

pc = pinecone.Pinecone(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV_NAME"),
)

vector_store = PineconeVectorStore.from_existing_index(
    os.getenv("PINECONE_INDEX_NAME"), embeddings
)


def build_retriever(document_id):
    """
    Build a retriever object using the PineconeVectorStore

    :return: A retriever object
    """
    search_kwargs = {"filter": {"document_id": document_id}}
    return vector_store.as_retriever(search_kwargs=search_kwargs)


def delete_document(document_id):
    """
    Delete a document from the PineconeVectorStore

    :param document_id: The document ID to delete
    """
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
    query = index.query(
        vector=[0] * 1536,  # A vector of zeros to get all the matches
        filter={"document_id": {"$eq": document_id}},
        top_k=10000,
        include_metadata=True,
    )
    ids_to_delete = [match.id for match in query.matches]
    if ids_to_delete:
        index.delete(ids_to_delete)


async def delete_document_async(document_id):
    """
    Delete a document from the PineconeVectorStore asynchronously

    :param document_id: The document ID to delete
    """
    loop = asyncio.get_event_loop()
    fut = loop.run_in_executor(None, delete_document, document_id)
    return await fut
