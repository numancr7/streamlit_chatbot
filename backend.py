from langgraph.graph import StateGraph, START , END , state
from typing import TypedDict , Annotated , List
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode , tools_condition
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.tools import Tool
from langchain.tools import tool
from dotenv import load_dotenv
import sqlite3
import requests
import os

# Load environment variables (works for local .env file)
load_dotenv()

# Try to import streamlit for cloud deployment (optional)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

# Get API key from Streamlit secrets (for cloud deployment) or environment variable (for local)
# Streamlit secrets take precedence if available
api_key = None
if STREAMLIT_AVAILABLE and hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
    api_key = st.secrets['OPENAI_API_KEY']
elif os.getenv('OPENAI_API_KEY'):
    api_key = os.getenv('OPENAI_API_KEY')

# Initialize LLM with API key if available
if api_key:
    llm = ChatOpenAI(api_key=api_key)
else:
    llm = ChatOpenAI()  # Falls back to environment variable or default

# Tools

#1.

wrapper = DuckDuckGoSearchAPIWrapper()
search_tool = Tool(
    name="duckduckgo_search",
    description="Search DuckDuckGo for recent results.",
    func=wrapper.run,
)

#2.

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


# 3.

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()

tools = [search_tool , get_stock_price , calculator]

llm_with_tools = llm.bind_tools(tools=tools)


class ChatSate(TypedDict):
    messages : Annotated[list[BaseMessage] , add_messages]


def chat_node(state : ChatSate):
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {'messages' : [response]}

tool_node = ToolNode(tools=tools)

conn = sqlite3.connect(database='chatbot.db' , check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatSate)

graph.add_node('chat_node' , chat_node)
graph.add_node('tools' , tool_node)

graph.add_edge(START , 'chat_node')
graph.add_conditional_edges('chat_node' , tools_condition)
graph.add_edge('tools' , 'chat_node')
graph.add_edge('chat_node' , END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)
