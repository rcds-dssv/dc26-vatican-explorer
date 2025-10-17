# this will be removed, and instead will be written by Arne.  I am using this to test my database.

import requests
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def get_all_speech_links(
        url: str, 
        include_substrings = ["/en/", "/documents/"], 
        exclude_substrings = ["/biography/"], 
        timeout: int = 10
) -> list[str]:
    """
    Fetch a page and return all links containing ANY of the given substrings.
    
    Parameters:
        url (str): The base URL of the page.
        include_substrings (str | list[str]): All substrings must match.
        exclude_substrings (str | list[str]): All substrings must not match.
        timeout (int): Timeout for the request (default 10s).
        
    Returns:
        list[str]: A list of absolute URLs following substring requirements.
    """

    soup = fetch_and_parse_web_content(url, timeout)
    links = []

    if isinstance(include_substrings, str):
        include_substrings = [include_substrings]  

    if isinstance(exclude_substrings, str):
        exclude_substrings = [exclude_substrings]  

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if all(sub in href for sub in include_substrings) and all(sub not in href for sub in exclude_substrings):
            full_url = urljoin(url, href) 
            links.append(full_url)

    return links



def fetch_and_parse_web_content(
        url: str, 
        timeout: int = 10
):
    """
    Fetches and returns the content of a website as soup.
    
    Parameters:
        url (str): The URL of the website to fetch.
        timeout (int): Timeout for the request (default 10s).

    Returns:
        soup: The content of the website as a BeautifulSoup object.
    
    Raises:
        requests.exceptions.RequestException: If there's an issue fetching the URL.
    """
    
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.0.0 Safari/537.36 "
            "vatican-explorer/1.0 (+https://github.com/rcds-dssv/dc26-vatican-explorer)"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding  # force best-guess decoding
    
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup


def parse_speech_metadata(soup) -> dict:
    """
    Parse a Vatican speech HTML page to extract metadata.

    Parameters:
        soup: Output from BeautifulSoup
    
    Returns:
        dict: like {"pope": "Francis", "name": "Angelus", "date": "04-13-2025", "special": "Palm Sunday"}
    """

    meta = soup.find("meta", attrs={"name": "description"})
    if not meta or "content" not in meta.attrs:
        return {}

    # Example: "POPE FRANCIS ANGELUS Palm Sunday, 13 April 2025 [ Multimedia ]"
    content = meta["content"].strip()
    content_list = content.split()

    # 1. Extract pope and name
    pope_index = content_list.index('POPE')
    try:
        pope = content_list[pope_index + 1].capitalize()
        name = content_list[pope_index + 2].capitalize()
    except:
        pope = name = None

    # 2. Extract the date
    year_index = None
    years = [str(i+1000) for i in range(2000)]
    for i,val in enumerate(content_list):
        if any(yr in val for yr in years):
            year_index = i
            break
    try:
        year = content_list[year_index]
        month = content_list[year_index - 1]
        day = content_list[year_index - 2]
        date = datetime.strptime(day + " " + month + " " + year, "%d %B %Y").strftime("%m-%d-%Y")
    except:
        date = None

    # 3. Extract special title (e.g., "Palm Sunday")
    # Assume this is between the name and the date
    try:
        i1 = pope_index + 3
        i2 = year_index - 2
        special = " ".join(content_list[i1:i2])
    except:
        special = None


    return {
        "pope": pope,
        "name": name,
        "date": date,
        "special": special,
    }


def extract_speech_text(soup) -> str:
    """
    Extracts all <p> text inside the Vatican speech <div class="text parbase vaticanrichtext">.
    Removes any nested HTML tags like <sup>, <i>, etc.

    Parameters:
        soup: Output from BeautifulSoup
    
    Returns:
        str:  single clean text string
    
    """

    # Find the div containing the main speech content
    div = soup.find("div", class_="text parbase vaticanrichtext")
    if not div:
        return ""

    paragraphs = []
    for p in div.find_all("p"):
        # Remove inline tags like <sup>, <a>, <i>, etc.
        for tag in p.find_all(True):
            tag.unwrap()
        text = p.get_text(strip=True)
        if text:
            paragraphs.append(text)

    # Join paragraphs with a blank space (or "\n\n" if you want paragraph breaks)
    return " ".join(paragraphs)

def get_speech_text(
    url: str, 
    timeout: int = 10       
) -> dict:
    """
    Fetches and returns the content a pope speech in dict format.
    
    Parameters:
        url (str): The URL of the website to fetch.
        timeout (int): Timeout for the request (default 10s).

    Returns:
        dict: like {"pope": "Francis", "name": "Angelus", "date": "04-13-2025", "special": "Palm Sunday", "speech": <text of speech>}
    
    """

    soup = fetch_and_parse_web_content(url, timeout)
    output = parse_speech_metadata(soup)
    output["text"] = extract_speech_text(soup)

    return output


if __name__ == "__main__":
    url = "https://www.vatican.va/content/francesco/en/angelus/2025.index.html"
    links = get_all_speech_links(url)

    test_url = links[0]
    speech_content = get_speech_text(test_url)

    print(speech_content)
    
