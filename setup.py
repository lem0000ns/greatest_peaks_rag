from langchain_community.document_loaders import DirectoryLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH = "chroma"
db = Chroma.from_documents(
    chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
)

DATA_PATH = "data/cleaned"

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.txt")
    documents = loader.load()
    return documents

def chunk_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks")
    return chunks

def main():
    documents = load_documents()
    chunks = chunk_documents(documents)
    print(chunks[0].page_content)
    print(chunks[0].metadata)

if __name__ == "__main__":
    main()