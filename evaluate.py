from rag_chain import get_qa_chain, get_retriever
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
    answer_correctness,
    answer_similarity
)
from ragas import evaluate
from datasets import Dataset
from dotenv import load_dotenv
import os
import openai

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']

questions = [
    "What three objects make up the Deathly Hallows?",
    "Why did Ron Weasley join the Gryffindor Quidditch team?",
    "What motivates Snape to protect Harry throughout the series?"
]

ground_truths = [
    "The Elder Wand, the Invisibility Cloak, and the Resurrection Stone",
    "Ron joined the Gryffindor Quidditch team as the Keeper during his fifth year after Oliver Wood graduated and Angelina Johnson held tryouts",
    "His enduring love for Lily Potter"
]

def create_ragas_dataset(rag_chain, retriever):
    answers = []
    contexts = []

    for query in questions:
        answers.append(rag_chain.invoke({"input": query})['answer'])
        contexts.append([doc.page_content for doc in retriever.get_relevant_documents(query)])
    
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "reference": ground_truths
    }
    dataset = Dataset.from_dict(data)
    return dataset

def evaluate_ragas_dataset(dataset):
    result = evaluate(
        dataset,
        metrics=[
            context_precision,
            faithfulness,
            answer_relevancy,
            context_recall,
            answer_correctness,
            answer_similarity
        ]
    )
    return result

if __name__ == "__main__":
    rag_chain = get_qa_chain()
    retriever, question_answer_chain = get_retriever()
    dataset = create_ragas_dataset(rag_chain, retriever)
    result = evaluate_ragas_dataset(dataset)
    print(result)