import asyncio
from concurrent.futures import ThreadPoolExecutor

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.chat.vector_store import vector_store


async def create_embeddings_for_pdf(document_id: int, document_path: str) -> None:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    loader = PyPDFLoader(document_path)

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        docs = await loop.run_in_executor(
            pool, lambda: loader.load_and_split(text_splitter)
        )

    for doc in docs:
        doc.metadata = {
            "document_id": document_id,
            "page": doc.metadata["page"],
            "text": doc.page_content,
        }
    await vector_store.aadd_documents(docs)
