import streamlit as st
import asyncio
import os
import sys
import time
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
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# -------------------- Initialize model_with_tools and tools --------------------
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
            "url": "http://127.0.0.1:8000/mcp"
        }
    }
)

# Load tools from MCP
tools = asyncio.run(client.get_tools())
model_with_tools = model_with_tools.bind_tools(tools)

# -------------------- Graph Definition --------------------
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
# Graph definition
# ---------------------------
graph = StateGraph(MessagesState)

def agent_node(state: MessagesState):
    """Agent node that calls the LLM and decides tools."""
    response = model_with_tools.invoke(state["messages"])
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
# Streamlit UI — Real Website Design
# ---------------------------
st.set_page_config(page_title="✈️ Travel Planner AI", page_icon="🌍", layout="wide")

# Custom CSS — Professional Website Look
st.markdown("""
    <style>
        :root {
            --primary: #4A90E2;
            --secondary: #2C3E50;
            --light: #F8F9FA;
            --dark: #121212;
            --success: #28a745;
            --warning: #ffc107;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--light);
            color: #333;
        }

        .sidebar .sidebar-content {
            background-color: var(--light);
            padding: 1rem;
            border-right: 1px solid #eee;
        }

        .stButton>button {
            background-color: var(--primary);
            color: white;
            border-radius: 8px;
            font-weight: 600;
            width: 100%;
            margin-top: 1rem;
            border: none;
            padding: 0.8rem;
            font-size: 1rem;
        }
        .stButton>button:hover {
            background-color: #357ABD;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }

        .result-card {
            background-color: white;
            padding: 2rem;
            border-radius: 16px;
            border-left: 5px solid var(--primary);
            margin: 2rem 0;
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
            font-size: 1.05rem;
            line-height: 1.7;
        }
        .result-card h1, .result-card h2, .result-card h3 {
            color: var(--secondary);
            margin-top: 1.5em;
            border-bottom: 1px solid #eee;
            padding-bottom: 0.5em;
        }
        .result-card ul, .result-card ol {
            padding-left: 1.5em;
        }
        .result-card a {
            color: var(--primary);
            text-decoration: none;
        }
        .result-card a:hover {
            text-decoration: underline;
        }

        .section-title {
            color: var(--secondary);
            border-bottom: 2px solid #eee;
            padding-bottom: 0.5rem;
            margin-top: 2rem;
            font-weight: 600;
        }

        .footer {
            text-align: center;
            margin-top: 4rem;
            color: #7f8c8d;
            font-size: 0.85rem;
            padding: 1rem;
            border-top: 1px solid #eee;
        }

        .header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .header img {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
        }

        .badge {
            display: inline-block;
            background-color: var(--primary);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 0.5rem;
        }

        /* Dark Mode */
        [data-theme="dark"] {
            --light: #121212;
            --dark: #1e1e1e;
            --primary: #5D9CEC;
            --secondary: #BDC3C7;
        }
        [data-theme="dark"] body {
            background-color: var(--dark);
            color: #e0e0e0;
        }
        [data-theme="dark"] .result-card {
            background-color: #1e1e1e;
            border-left-color: var(--primary);
            color: #e0e0e0;
        }
        [data-theme="dark"] .result-card h1, .result-card h2, .result-card h3 {
            color: var(--secondary);
        }
        [data-theme="dark"] .result-card a {
            color: #85c1e9;
        }
        [data-theme="dark"] .stButton>button {
            background-color: var(--primary);
        }
        [data-theme="dark"] .stButton>button:hover {
            background-color: #4a83c0;
        }
        [data-theme="dark"] .sidebar .sidebar-content {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border-right-color: #333;
        }
        [data-theme="dark"] .footer {
            color: #aaa;
            border-top-color: #333;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.image("C:/Users/VICTUS/Desktop/Agent/Langchain_Agent/Website/2461656.jpg", width=200)
    st.markdown("<h1 class='sidebar-title'>✈️ Travel Planner AI Pro</h1>", unsafe_allow_html=True)
    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    st.subheader("📍 Trip Details")
    city_input = st.text_input("Primary Destination", placeholder="e.g., Tokyo", value="Paris")
    additional_cities = st.text_input("Additional Destinations (comma separated)", placeholder="e.g., Kyoto, Osaka")
    duration = st.slider("Trip Duration (days)", 1, 30, 7)
    season = st.selectbox("Season", ["summer", "winter", "rainy"], index=0)

    st.subheader("🛂 Traveler Profile")
    nationality = st.text_input("Your Nationality", placeholder="e.g., United States", value="United States")
    budget = st.number_input("Total Budget (in any currency)", min_value=100, value=2000, step=100)
    budget_currency = st.selectbox("Budget Currency", ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "INR", "CHF"], index=0)

    st.subheader("🌐 Language & Theme")
    translate_to = st.selectbox("Translate Output To", ["None", "hi", "es", "fr", "de", "ja", "zh"], index=0)
    theme = st.radio("Theme", ["Light", "Dark"], horizontal=True, key="theme_radio")

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)
    st.subheader("⚙️ Settings")
    st.caption("⚡ Powered by Mistral-7B & OpenRouter")
    st.caption("📡 Data: Nominatim, Open-Meteo, Exchangerate.host, Wikipedia, DuckDuckGo")
    st.caption("✅ Auto-tool selection enabled")

    if st.button("🔄 Reset Plan", type="secondary"):
        st.session_state.clear()

# Theme handling
if theme == "Dark":
    st.markdown('<div data-theme="dark">', unsafe_allow_html=True)
else:
    st.markdown('<div data-theme="light">', unsafe_allow_html=True)

# --- Custom Styling with Animation ---
st.markdown("""
    <style>
        /* Sidebar Title */
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            color: #4CAF50;
            animation: fadeIn 1.2s ease-in-out;
        }

        /* Divider with Glow */
        .sidebar-divider {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, #4CAF50, #00BCD4);
            margin: 10px 0;
            animation: glow 2s infinite alternate;
        }

        /* Inputs animation */
        .stTextInput, .stNumberInput, .stSelectbox, .stRadio {
            animation: slideIn 0.8s ease;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-15px); }
            to { opacity: 1; transform: translateX(0); }
        }
        @keyframes glow {
            from { box-shadow: 0 0 5px #4CAF50; }
            to { box-shadow: 0 0 15px #00BCD4; }
        }
    </style>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
        .header {
            display: flex;
            align-items: center;
            gap: 15px;
            background-color: #1E1E1E;
            padding: 15px;
            border-radius: 12px;
        }
        .header h1 {
            color: #EAEAEA;
            margin: 0;
        }
        .badge {
            background: #4CAF50;
            color: white;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 12px;
            margin-left: 8px;
        }
        .header img {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            object-fit: cover;
        }
    </style>

    <div class="header">
        <img src="https://www.google.com/imgres?q=travel%20planner%20agent%20logo&imgurl=https%3A%2F%2Fstatic.vecteezy.com%2Fsystem%2Fresources%2Fpreviews%2F005%2F183%2F355%2Fnon_2x%2Ftravel-agency-logo-template-holiday-logo-template-beach-logo-concept-vector.jpg&imgrefurl=https%3A%2F%2Fwww.vecteezy.com%2Ffree-vector%2Ftravel-agency-logo&docid=YNGTmPqtgb2JWM&tbnid=DVOybeNNWt0HrM&vet=12ahUKEwj2jPjYx9ePAxUZh1YBHTJqENEQM3oECCAQAA..i&w=980&h=980&hcb=2&ved=2ahUKEwj2jPjYx9ePAxUZh1YBHTJqENEQM3oECCAQAA" alt="Logo">
        <div>
            <h1>🌍 AI Travel Planner Pro</h1>
            <span class="badge">Enterprise Edition</span>
        </div>
    </div>
""", unsafe_allow_html=True)


st.write("""
    **Your ultimate AI travel assistant** — generates personalized, detailed, and legally compliant travel plans with:
    - ✈️ Real flight searches  
    - 💰 Budget conversion to local currency  
    - 🛂 Visa & entry rules by nationality  
    - 📜 City-specific regulations (dress codes, photography, drones, alcohol)  
    - 🏨 Top 10 hotels & attractions  
    - ☀️ 3-day weather forecasts  
    - 🧳 Smart packing lists  
    - 📚 Wikipedia cultural insights  
    - 🔍 DuckDuckGo real-time updates & hidden gems  
    - 🇮🇳 Translation to any language
""")

# Multi-city prompt builder
destinations = [city_input.strip()] + [c.strip() for c in additional_cities.split(",") if c.strip()]
all_destinations = ", ".join(destinations) if destinations else city_input

# 🔥 CRITICAL: Force LLM to use ALL relevant tools with explicit instructions
prompt_template = f"""
You are an expert travel planner AI. Create a {duration}-day travel guide 
for {nationality} visiting {all_destinations} during {season}, with a total 
budget of {budget} {budget_currency} (convert into local currencies).

⚙️ USE TOOLS IN ORDER:
1. `place_finder`: Top 10 hotels + 10 attractions per city.  
   - For attractions: why unique, how to reach, transport cost/time, best visiting hours, ticket rules, nearby food.  
2. `weather_forecast`: {duration}-day forecast per city.  
3. `packing_list`: Clothing suggestions.  
4. `currency_converter`: Convert {budget} {budget_currency} to each city.  
5. `duckduckgo_search`: Safety tips per city.  
6. `DuckDuckGoSearchResults`: Flights, advisories, laws, hidden gems, festivals, gov docs.  
7. Fallback to `flight_info` if flights missing.  
8. `WikipediaQueryRun`: Cultural/historical context.  
9. `translator`: Translate final guide into {translate_to} (if needed).

📑 OUTPUT STRUCTURE:
# 🌍 Travel Guide: {all_destinations}

- **Itinerary Overview**: trip duration, cities, traveler profile.  
- **Budget Breakdown**: {budget} {budget_currency} → local currencies, daily costs, leftover.  
- **Entry & Visa Rules**: Visa (Y/N), e-Visa, passport validity, health forms.  
- **Docs & Links**: Embassy, emergency nos, transport apps, govt advisories.  
- **Laws & Regulations**: Dress code, photography, alcohol/drugs, public norms, drones, internet rules.  
- **Hotels & Attractions**: Top 10 hotels + 10 attractions with details.  
- **Transport Guide**: metro/bus/taxi/walking in 5 lines.  
- **Weather Forecast**: {duration}-day per city.  
- **Packing List**: 3 lines clothing tips.  
- **Flights**: Airlines, prices, durations, booking links.  
- **Cultural Insights**: 1–2 key facts per city.  
- **Local Tips & Hidden Gems**: Festivals, markets, free-entry days.  
- **Final Notes**: Safety, respect traditions, offline maps, embassy registration.  

Translate full guide if requested.
"""


# Button to trigger planning
if st.button("🚀 Generate My Travel Plan", use_container_width=True):
    if not city_input.strip():
        st.error("⚠️ Please enter at least one destination.")
    else:
        with st.spinner("🧠 AI is researching your trip across 10+ sources... This may take 20–60 seconds."):
            start_time = time.time()
            try:
                final = app.invoke({"messages": [("user", prompt_template)]})
                last_msg = final["messages"][-1]
                answer = last_msg.content if isinstance(last_msg.content, str) else str(last_msg.content)

                elapsed = time.time() - start_time
                st.success(f"✅ Plan generated in {elapsed:.1f} seconds!")

                # Display result as rich Markdown card
                # CSS
                st.markdown("""
                    <style>
                        .result-card {
                            background-color: #1E1E1E;  /* Dark gray background */
                            color: #EAEAEA;  /* Light text for contrast */
                            padding: 20px;
                            border-radius: 12px;
                            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5);
                            font-size: 16px;
                            line-height: 1.6;
                            font-family: 'Segoe UI', sans-serif;
                            border: 1px solid #333;
                            transition: transform 0.2s ease, box-shadow 0.2s ease;
                        }
                        .result-card:hover {
                            transform: scale(1.02);
                            box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.7);
                        }
                    </style>
                """, unsafe_allow_html=True)

                # HTML content
                st.markdown(f"""
                    <div class="result-card">
                        {answer}
                    </div>
                """, unsafe_allow_html=True)



                # ✅ DOWNLOAD BUTTON
                st.download_button(
                    label="📥 Download Travel Plan as TXT",
                    data=answer,
                    file_name=f"travel_plan_{city_input.replace(' ', '_')}_Pro.txt",
                    mime="text/plain",
                    use_container_width=True
                )

                # Show usage stats
                tool_calls = sum(1 for msg in final["messages"][:-1] if hasattr(msg, 'tool_calls') and msg.tool_calls)
                st.info(f"📊 Used {tool_calls} tools across {len(final['messages']) - 1} steps.")

            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.exception(e)

# Close theme div
st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<div class='footer'>© 2025 Travel Planner AI Pro | Powered by OpenRouter & LangGraph • Built with ❤️ for Global Citizens</div>", unsafe_allow_html=True)