from mcp.server.fastmcp import FastMCP

from transformers import pipeline

# ---- LangChain Native Tools (REPLACES manual imports) ----
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools.wikipedia.tool import WikipediaQueryRun

# ---- Transformers for translation ----
from transformers import pipeline
import requests
# -------------------- Initialize MCP --------------------
mcp = FastMCP("travel_planner_app")
print("\n🚀 MCP Initialized\n")

# -------------------- Math Tools --------------------
# Translation tool
translator_pipeline = pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi")

@mcp.tool(description="Translate text to a specified language.")
def translator(text: str, language: str = "hi") -> str:
    """Translate travel info to target language."""
    print(f"\n🔧 Using translator tool to translate to {language}\n")
    try:
        if language == "hi":
            result = translator_pipeline(text, max_length=512)
            return result[0]['translation_text']
        else:
            model_name = f"Helsinki-NLP/opus-mt-en-{language}"
            trans = pipeline("translation", model=model_name)
            result = trans(text, max_length=512)
            return result[0]['translation_text']
    except Exception as e:
        return f"[Translation error: {e}]\n{text}"


@mcp.tool(description="Find places like hotels, restaurants, or attractions in a given location.")
def place_finder(place: str, category: str = "hotel") -> str:
    """Find hotels, restaurants, or attractions in a given place using OpenStreetMap."""
    print(f"\n🔧 Using place_finder tool for {category} in {place}\n")
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{category} in {place}", "format": "json", "limit": 5}
    headers = {"User-Agent": "TravelPlannerApp"}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    if not data:
        return f"⚠️ No {category}s found in {place}"

    results = [f"- {item['display_name']}" for item in data]
    return f"📍 {category.title()}s in {place}:\n" + "\n".join(results)


@mcp.tool(description="Get a 3-day weather forecast for a city.")
def weather_forecast(city: str) -> str:
    """Get a 3-day weather forecast for a city."""
    print(f"\n🔧 Using weather_forecast tool for {city}\n")
    url = "https://geocoding-api.open-meteo.com/v1/search"
    geo = requests.get(url, params={"name": city}).json()
    if not geo.get("results"):
        return f"⚠️ Could not find location for {city}"
    
    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    forecast_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min",
        "forecast_days": 3,
        "timezone": "auto"
    }
    weather = requests.get(forecast_url, params=params).json()

    days = weather["daily"]["time"]
    max_temps = weather["daily"]["temperature_2m_max"]
    min_temps = weather["daily"]["temperature_2m_min"]

    forecast = "\n".join([f"{d}: {mn}°C - {mx}°C" for d, mn, mx in zip(days, min_temps, max_temps)])
    return f"🌤 3-day forecast for {city}:\n{forecast}"


@mcp.tool(description="Convert amount between currencies.")
def currency_converter(amount: float, from_currency: str, to_currency: str = "USD") -> str:
    """Convert amount between currencies."""
    print(f"\n🔧 Using currency_converter tool: {amount} {from_currency} → {to_currency}\n")
    url = f"https://api.exchangerate.host/convert"
    params = {"from": from_currency, "to": to_currency, "amount": amount}
    response = requests.get(url, params=params).json()
    if "result" not in response:
        return "⚠️ Conversion failed"
    return f"{amount} {from_currency} = {response['result']} {to_currency}"


@mcp.tool(description="Get flight information between two cities.")
def flight_info(source: str, destination: str) -> str:
    """Mock flight info (replace with real API like Skyscanner/Amadeus for production)."""
    print(f"\n🔧 Using flight_info tool for {source} → {destination}\n")
    return f"✈️ Example flights from {source} to {destination}:\n- Airline A: $350 (6h)\n- Airline B: $420 (non-stop)\n- Airline C: $300 (1 stop)"


@mcp.tool(description="Fetch latest travel advisory for a city.")
def travel_advisory(city: str) -> str:
    """Fetch latest travel advisory (mock version)."""
    print(f"\n🔧 Using travel_advisory tool for {city}\n")
    return f"⚠️ Always check your embassy website for advisories before traveling to {city}."


@mcp.tool(description="Suggest a simple packing list based on season.")
def packing_list(city: str, season: str = "summer") -> str:
    """Suggest a simple packing list based on season."""
    print(f"\n🔧 Using packing_list tool for {city} in {season}\n")
    lists = {
        "summer": ["T-shirts", "Shorts", "Sunscreen", "Hat", "Light shoes"],
        "winter": ["Jacket", "Sweater", "Gloves", "Scarf", "Boots"],
        "rainy": ["Raincoat", "Umbrella", "Waterproof shoes"]
    }
    items = lists.get(season.lower(), ["General clothes", "Shoes", "Toiletries"])
    return f"🧳 Suggested packing list for {city} in {season}:\n- " + "\n- ".join(items)



if __name__ == "__main__":
    mcp.run(transport="streamable-http")
