from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Reuse your LangGraph "app" (compiled graph)
from model import app as travel_graph   # 👈 import your LangGraph app

app = FastAPI()

# Static + Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/plan", response_class=HTMLResponse)
async def plan_trip(
    request: Request,
    destination: str = Form(...),
    days: int = Form(...),
    travelers: str = Form(...),
    interests: str = Form(...),
    budget: str = Form(...),
):
    user_prompt = f"""
    You are a professional travel planner. 
    Plan a {days}-day trip to {destination} for {travelers}. 

    Include:
    - Morning, Afternoon, Evening activities
    - Food recommendations
    - Estimated budget per day
    - Travel tips
    - Alternatives for rainy/rest days
    - Packing checklist at the end

    ⚠️ Output format requirement:
    Return the response in **pure HTML** using <div>, <h3>, <ul>, <li>, <p> etc. 
    Do not include Markdown (#, ##) or extra text outside HTML.
    The HTML must be clean and ready to insert inside an itinerary container.
    """


    result = travel_graph.invoke({"messages": [("user", user_prompt)]})
    print("🗺️ Trip planned!",result)

    # Extract final model response
    last_msg = result["messages"][-1]
    itinerary_text = last_msg.content if isinstance(last_msg.content, str) else str(last_msg.content)

    # Split itinerary into list items (simple heuristic)
    itinerary = [line.strip() for line in itinerary_text.split("\n") if line.strip()]
    print("📋 Itinerary:", itinerary)

    return templates.TemplateResponse(
        "itinerary.html",
        {
            "request": request,
            "destination": destination,
            "days": days,
            "travelers": travelers,
            "interests": interests,
            "budget": budget,
            "itinerary": itinerary,
        },
    )
