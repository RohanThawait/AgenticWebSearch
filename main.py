from fastapi import FastAPI
from pydantic import BaseModel
from serpapi import GoogleSearch
import os

app = FastAPI()

# Define the input model
class QueryRequest(BaseModel):
    query: str

# Load API Key from Environment Variable (or set it directly)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def search_google(query):
    """Fetch search results using SerpAPI."""
    search = GoogleSearch({
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 5  # Fetch top 5 results
    })
    results = search.get_dict()
    
    # Extract relevant search results
    search_results = []
    for result in results.get("organic_results", []):
        search_results.append({
            "title": result.get("title"),
            "link": result.get("link"),
            "snippet": result.get("snippet")
        })
    
    return search_results


@app.get("/")
def home():
    return {"message": "AI Search Agent API is running!"}

# Endpoint to receive queries
@app.post("/search/")
def search_web(request: QueryRequest):
    query = request.query
    search_results = search_google(query)
    return {"query": query, "results": search_results}

# Run using: uvicorn main:app --reload
