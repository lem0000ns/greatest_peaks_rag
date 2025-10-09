from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
import argparse
from rag_chain import get_qa_chain
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
import os
from langchain_openai import ChatOpenAI

load_dotenv()

search = GoogleSerperAPIWrapper()

rag_chain = get_qa_chain()
with open("input_players.txt", "r") as f:
    input_players = f.read()


def rag_tool_func(q):
    print(f"\nRAG tool called with question: {q}")
    return rag_chain.invoke({"input": q})

tools = [
    Tool(
        name="RAG",
        func=rag_tool_func,
        description=f"Use this FIRST to answer questions about NBA players. Contains detailed information about: {input_players}."
    ),
    Tool(
        name="Google Search",
        description="Use ONLY if RAG cannot provide sufficient information. Search the web for additional details. Input should be a search query.",
        func=search.run,
    )
]

REACT_PROMPT = """You are a helpful assistant that answers questions about NBA players. You have access to the following tools:
{tools}

IMPORTANT INSTRUCTIONS:
1. ALWAYS try the RAG tool FIRST for any question about NBA players
2. Only use Google Search if RAG cannot provide sufficient information
3. Once a final answer is found, STOP and provide the Final Answer immediately

To use a tool, you MUST use the following format:
1. Thought: Do I need to use a tool? Yes
2. Action: the action to take, should be one of [{tool_names}]
3. Action Input: the input to the action
4. Observation: the result of the action

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the following format:
1. Thought: Do I need to use a tool? No
2. Final Answer: [your response here]

It's very important to always include the 'Thought' before any 'Action' or 'Final Answer'. Ensure your output strictly follows the formats above.

Begin!

Previous conversation history:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}
"""


def get_agent_chain():
    prompt = PromptTemplate.from_template(REACT_PROMPT)
    agent = create_react_agent(llm=ChatOpenAI(model_name='gpt-4-turbo'), tools=tools, prompt=prompt)
    memory = ConversationBufferWindowMemory(memory_key='chat_history', k=5, return_messages=True, output_key="output")
    agent_chain = AgentExecutor(agent=agent,
                            tools=tools,
                            memory=memory,
                            max_iterations=5,
                            handle_parsing_errors=True,
                            verbose=True,
                            )
    return agent_chain

def main():
    agent_chain = get_agent_chain()
    while True:
        user_query = input("> ")
        if user_query == "q":
            break
        # use agent chain to simulate conversation
        response = agent_chain.invoke({"input": user_query})
        print(response['output'])
    print("Goodbye!")

if __name__ == "__main__":
    main()