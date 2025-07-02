# import requests
# from bs4 import BeautifulSoup

# def get_medium_story_text(medium_url: str) -> str:
#     response = requests.get(medium_url)
#     if response.status_code != 200:
#         raise Exception(f"Failed to load page: {response.status_code}")

#     soup = BeautifulSoup(response.content, "html.parser")

#     # Extract title
#     title_tag = soup.find("h1")
#     title = title_tag.text if title_tag else "Untitled"

#     # Extract paragraphs
#     paragraphs = soup.find_all("p")
#     content = "\n\n".join(p.get_text() for p in paragraphs)

#     full_text = f"# {title}\n\n{content}"
#     return full_text

from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
import json

def get_medium_story_text(url: str) -> str:
    """
    Fetch and extract the main content from a Medium story URL
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main article content
        article = soup.find('article')
        if not article:
            return "Could not find article content"
        
        # Extract all paragraphs
        paragraphs = article.find_all('p')
        
        # Combine paragraphs into a single string
        content = '\n\n'.join([p.get_text() for p in paragraphs])
        
        return content
        
    except requests.RequestException as e:
        return f"Error fetching Medium story: {str(e)}"
    except Exception as e:
        return f"Error processing Medium story: {str(e)}"
