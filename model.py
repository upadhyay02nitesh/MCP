import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

# -------------------- Load environment --------------------
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

# Fix asyncio event loop for Windows
import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# -------------------- Initialize model_with_tools and tools --------------------
# Initialize model_with_tools
model_with_tools = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0.7,
    max_tokens=1000
)

# Connect to your MCP server
client = MultiServerMCPClient(
    {
        "travel_planner_app": {
            "transport": "streamable_http",
            "url": "http://127.0.0.1:8000/mcp_cust"
        }
    }
)

# Load tools from MCP (must be run in an event loop)
import asyncio
tools = asyncio.run(client.get_tools())
model_with_tools = model_with_tools.bind_tools(tools)

# -------------------- Async function to run LangGraph --------------------
async def run_graph(user_input: str):
    pass  # Function body can be implemented as needed

# ---------------------------
# Graph definition
# ---------------------------
graph = StateGraph(MessagesState)

def agent_node(state: MessagesState):
    """Agent node that calls the model_with_tools and decides tools."""
    print("\n🤖 Agent is processing the request...")
    response = model_with_tools.invoke(state["messages"])
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"\n🛠️ Agent decided to use tools: {[t['name'] for t in response.tool_calls]}")
    
    return {"messages": [response]}

def tools_condition(state: MessagesState):
    last_msg = state["messages"][-1]
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        return "tools"
    return END

graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
graph.add_edge("agent", END)

app = graph.compile()

# ---------------------------
# Demo run
# ---------------------------
if __name__ == "__main__":
    user_city = "Paris"
    user_prompt = f"""
    I want to travel to {user_city}. Suggest main attractions, explain in Hindi, 
    give me a packing list for summer, check weather, and find hotels.
    """

    print("\n--- Running Travel Planner Agent ---\n")
    print(f"User prompt: {user_prompt}\n")

    final = app.invoke({"messages": [("user", user_prompt)]})

    last_msg = final["messages"][-1]
    answer = last_msg.content if isinstance(last_msg.content, str) else str(last_msg.content)

    print("\n--- Final Travel Plan ---\n")
    print(answer)
    print("\n🌍 Note: This assistant provides travel tips and info only. Always check latest local advisories before travel.\n")
