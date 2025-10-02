from langchain_community.document_loaders import DirectoryLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import openai
import os
import shutil

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']

CHROMA_PATH = "./chroma"

DATA_PATH = "data/4_groups"

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt")
    documents = loader.load()
    return documents

def chunk_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=500,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks")
    print(chunks[0].page_content)
    print(chunks[0].metadata)
    print("-"*100)
    print(chunks[1].page_content)
    print(chunks[1].metadata)
    return chunks

def store_chroma(chunks: list[Document]):
    # clear database first
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    # create new database from documents
    vectorstore = Chroma(collection_name="greatest_peaks_collection", persist_directory=CHROMA_PATH, embedding_function=OpenAIEmbeddings())
    vectorstore.add_documents(chunks)
    print(f"Stored {len(chunks)} chunks in {CHROMA_PATH}")

def main():
    documents = load_documents()
    chunks = chunk_documents(documents)
    store_chroma(chunks)

if __name__ == "__main__":
    main()