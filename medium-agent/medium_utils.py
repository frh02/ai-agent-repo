import requests
from bs4 import BeautifulSoup

def get_medium_story_text(medium_url: str) -> str:
    response = requests.get(medium_url)
    if response.status_code != 200:
        raise Exception(f"Failed to load page: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract title
    title_tag = soup.find("h1")
    title = title_tag.text if title_tag else "Untitled"

    # Extract paragraphs
    paragraphs = soup.find_all("p")
    content = "\n\n".join(p.get_text() for p in paragraphs)

    full_text = f"# {title}\n\n{content}"
    return full_text