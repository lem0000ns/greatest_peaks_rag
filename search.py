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

tools = [
    Tool(
        name="RAG",
        func=rag_chain.invoke,
        description="Useful when you're asked Retrieval Augmented Generation(RAG) related questions"
    ),
    Tool(
        name="Google Search",
        description="For answering questions that need current information (e.g. current players) or when you don't know the answer, use Google search to find the answer",
        func=search.run,
    )
]

CHARACTER_PROMPT = """Answer the following questions as best you can. You have access to the following tools:
{tools}

For any questions requiring tools, you should first search the provided knowledge base. If you don't find relevant information from provided knowledge base, then use Google search to find related information.

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
    print(response.keys())
    print("-" * 100)
    print(response['output'])

if __name__ == "__main__":
    main()