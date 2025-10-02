from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import openai
import os
import argparse

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']

CHROMA_PATH = "./chroma"
PROMPT_TEMPLATE = """
Answer the question based only on the following context: \n
{context}

Question: {question}

Answer:
"""

def print_docs_information(query_results):
    print("\nLength of query results: ", len(query_results))
    for i, result in enumerate(query_results):
        print(f"Relevance score of result {i+1}: ", result[1])
        print(f"Content of result {i+1}: ", result[0])
        print("-" * 100)

def retrieve_response(user_query):
    vectorstore = Chroma(collection_name="greatest_peaks_collection", persist_directory=CHROMA_PATH, embedding_function=OpenAIEmbeddings())
    results = vectorstore.similarity_search_with_relevance_scores(user_query, k=3)
    if len(results) == 0 or results[0][1] < 0.5:
        return "I'm sorry, I don't have information on that topic."
    sources = [result[0].metadata["source"] for result in results]
    context = "\n\n---\n\n".join([result[0].page_content for result in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context, question=user_query)
    print_docs_information(results)

    model = ChatOpenAI()
    response_text = model.invoke(prompt)

    return response_text.content, sources

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, type=str)
    args = parser.parse_args()
    user_query = args.query
    response, sources = retrieve_response(user_query)
    print(response)
    print("Sources: ", sources)

if __name__ == "__main__":
    main()