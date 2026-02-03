
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def scrape_wikipedia_poi(city: str) -> List[Dict[str, str]]:
    """
    Scrapes basic points of interest from Wikipedia.
    """
    headers = {
        'User-Agent': 'TravelSmartMVP/1.0 (contact: info@travelsmart.ai)'
    }
    url = f"https://en.wikipedia.org/wiki/{city.replace(' ', '_')}"
    activities = []
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract landmarks (heuristic: look for paragraphs or lists near 'Landmarks' or 'Tourism')
            # For MVP, we extract the first 5-8 bold items or list items in the main content
            content = soup.find(id="mw-content-text")
            if content:
                items = content.find_all(['li', 'b'], limit=30)
                for item in items:
                    text = item.get_text().strip()
                    if 5 < len(text) < 50: # Avoid noise
                        activities.append({
                            "nombre": text,
                            "fuente": "Wikipedia",
                            "url": url
                        })
                        if len(activities) >= 15: break
    except Exception as e:
        print(f"Scraping error: {e}")
        
    return activities
