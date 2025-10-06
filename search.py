from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv
import argparse
from rag_chain import get_qa_chain
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts.prompt import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
import os
from langchain_openai import ChatOpenAI
from get_data import input_players

load_dotenv()

search = GoogleSerperAPIWrapper()

rag_chain = get_qa_chain()

input_players = ", ".join([player.capitalize() for player in input_players.split(",")])
print(input_players)

tools = [
    Tool(
        name="RAG",
        func=lambda input, **kwargs: rag_chain.invoke(
            {"input": input, "chat_history": kwargs.get("chat_history", [])}
        ),
        description=f"Use this FIRST to answer questions about NBA players. Contains detailed information about: {input_players}. Input should be your question about these players."
    ),
    Tool(
        name="Google Search",
        description="Use ONLY if RAG cannot provide sufficient information. Search the web for additional details. Input should be a search query.",
        func=search.run,
    )
]

CHARACTER_PROMPT = """You are a helpful assistant that answers questions about NBA players. You have access to the following tools:
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
    prompt = PromptTemplate.from_template(CHARACTER_PROMPT)
    agent = create_react_agent(llm=ChatOpenAI(model_name='gpt-4o-mini'), tools=tools, prompt=prompt)
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
    # get query from command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, type=str)
    args = parser.parse_args()
    user_query = args.query

    # use agent chain to simulate conversation
    agent_chain = get_agent_chain()
    response = agent_chain.invoke({"input": user_query})
    print(response['output'])

if __name__ == "__main__":
    main()