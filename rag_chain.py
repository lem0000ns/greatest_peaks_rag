from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import openai
import os
import argparse

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']

CHROMA_PATH = "./chroma"

PROMPT_TEMPLATE = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

def print_docs_information(query_results):
    print("\nLength of query results: ", len(query_results))
    for i, result in enumerate(query_results):
        print(f"Relevance score of result {i+1}: ", result[1])
        print(f"Content of result {i+1}: ", result[0])
        print("-" * 100)

def get_qa_chain():
    vectorstore = Chroma(collection_name="greatest_peaks_collection", persist_directory=CHROMA_PATH, embedding_function=OpenAIEmbeddings())

    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_TEMPLATE),
        ("user", "{input}"),
    ])
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    question_answer_chain = create_stuff_documents_chain(llm=ChatOpenAI(model_name='gpt-4o-mini'), prompt=rag_prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    return rag_chain