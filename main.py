from fastapi import FastAPI
from pydantic import BaseModel
from serpapi import GoogleSearch
import os
import requests
from bs4 import BeautifulSoup
import openai

app = FastAPI()

# Define the input model
class QueryRequest(BaseModel):
    query: str

# Load API Key from Environment Variable (or set it directly)
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")


def search_google(query):
    """Fetch search results using SerpAPI."""
    search = GoogleSearch({
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 3  # Fetch top 3 results
    })
    results = search.get_dict()
    # Extract relevant search results
    search_results = []
    for result in results.get("organic_results", []):
        url = result.get("link")
        extracted_content = scrape_website(url) if url else None
        summary = summarize_text(extracted_content) if extracted_content else "No content available"
        
        search_results.append({
            "title": result.get("title"),
            "link": url,
            "snippet": result.get("snippet"),
            "content": extracted_content,
            "summary": summary
        })
    return search_results

def scrape_website(url):
    """Extracts text content from a webpage."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract text from common content areas
        paragraphs = soup.find_all("p")
        extracted_text = " ".join([p.get_text() for p in paragraphs])
        
        return extracted_text[:2000]  # Limit to first 2000 characters
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

def summarize_text(text):
    """Summarize text using OpenAI API."""
    try:
        openai.api_key = OPENAI_API_KEY
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Summarize the following content in 3-4 sentences."},
                      {"role": "user", "content": text}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error summarizing: {str(e)}"

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
