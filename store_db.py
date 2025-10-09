from langchain_community.document_loaders import DirectoryLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import openai
import os
import shutil
from scrape_hp import Scraper

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']

CHROMA_PATH = "./chroma"

DATA_PATH = "hp_data"

def chunk_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=500,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks")
    return chunks

# clear hp_data after each batch
def clear_data_folder():
    if os.path.exists(DATA_PATH):
        shutil.rmtree(DATA_PATH)
    os.makedirs(DATA_PATH)
    print(f"Cleared {DATA_PATH} folder")

def store_chroma_callback(vectorstore: Chroma):
    chunks = chunk_documents()
    vectorstore.add_documents(chunks)
    print(f"Stored {len(chunks)} chunks in {CHROMA_PATH}")

    clear_data_folder()

def main():
    # clear temporary text file storage
    clear_data_folder()

    # clear chroma database first
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    # create new database from documents
    vectorstore = Chroma(collection_name="harry_potter_collection", persist_directory=CHROMA_PATH, embedding_function=OpenAIEmbeddings())

    scraper = Scraper(batch_size=10, store_callback=lambda: store_chroma_callback(vectorstore))
    scraper.retrieve_places()

    clear_data_folder()

if __name__ == "__main__":
    main()