import os
import requests
import re
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urlparse
import time

def print_results(results, query):
    print(f"\nResults for search query: {query}")
    for i, (domain, title, text) in enumerate(results, start=1):
        print(f"{i}. [{title}]({domain})")
        print(f"Summary:\n{text}\n")

def is_valid_link(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def search_github(query):
    # Define the search URL
    url = f'https://github.com/search?q={urllib.parse.quote(query)}&type=Repositories'

    # Load the existing visited domains or initialize an empty list
    visited_domains = []
    if os.path.exists('visited_domains.txt'):
        with open('visited_domains.txt', 'r') as f:
            visited_domains = [line.strip() for line in f.readlines()]

    # Initialize a list to store the results
    results = []

    # Send a GET request to the URL
    print(f"Searching: {url}\n")
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the search result divs
    search_result_divs = soup.find_all('article', {'class': 'Box-row'})

    # Find the first 10 search results
    for search_result_div in search_result_divs[:10]:
        link_tag = search_result_div.find('h1', {'class': 'h3 lh-condensed'}).a

        # Get the link
        href = link_tag.get('href')

        # Extract the domain and title
        domain = urlparse(href).netloc
        title = link_tag.get_text(strip=True)

        # Print the link found
        print(f"Found link: {domain}")

        # Check if the link is from a preferred domain
        if domain not in visited_domains:
            if is_valid_link(f"http://{domain}"):
                # Get information from the website (specific information)
                response.close()
                response = requests.get(f"http://{domain}")
                response.encoding = 'utf-8'
                text_content = response.text

                # Save the result
                results.append((domain, title, text_content))

    return results

import wikipedia
import requests
from bs4 import BeautifulSoup
import warnings
import time
from urllib.parse import urlparse
import re

warnings.filterwarnings("ignore", category=UserWarning, module="bs4")

def extract_text_from_url(url):
    try:
        # Parse the URL to extract the page title
        parsed_url = urlparse(url)
        title = parsed_url.path.split('/')[-1].replace('_', ' ')

        # Get the Wikipedia page for the title
        page = wikipedia.page(title)

        # Get the title, summary, and URL of the Wikipedia page
        title = page.title
        summary = page.summary

        # Send a GET request to the URL
        response = requests.get(url)

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the text content of the Wikipedia page
        text_content = soup.find('div', {'id': 'bodyContent'}).get_text()

        return title, summary, text_content

    except wikipedia.exceptions.PageError as e:
        print(f"Error: {e}")
        return None, None, None

def search(query):
    # Initialize a list to store the results
    results = []

    if query.startswith("https://en.wikipedia.org/wiki/"):
        # If the query is a Wikipedia URL, extract text from the URL
        title, summary, text_content = extract_text_from_url(query)
        if title:
            results.append((title, summary, text_content))
    else:
        try:
            # Get the Wikipedia page for the query
            page = wikipedia.page(query, auto_suggest=True)

            # Get the title, summary, and URL of the Wikipedia page
            title = page.title
            summary = page.summary

            # Construct the URL using the title
            url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

            # Print the link found
            print(f"Found link: {url}")

            # Send a GET request to the URL
            response = requests.get(url)

            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the text content of the Wikipedia page
            text_content = soup.find('div', {'id': 'bodyContent'}).get_text()

            # Save the result
            results.append((title, summary, text_content))

        except wikipedia.exceptions.DisambiguationError as e:
            # Print a more informative message for the user
            print(f"The search query '{query}' is ambiguous. Please be specific or try one of the following options:")
            for option in e.options:
                print(f"- {option}")
            return

        except wikipedia.PageError as e:
            # Print a more informative message for the user
            print(f"Error: Wikipedia page for '{query}' not found. Please check the spelling or try a different query.")
            suggestions = wikipedia.search(query)
            if suggestions:
                print("Did you mean any of these:")
                for suggestion in suggestions:
                    print(f"- {suggestion}")
            return

        except (wikipedia.WikipediaException, wikipedia.exceptions.DisambiguationError) as e:
            time.sleep(0.5)

    # Print the results
    if not results:
        print("No relevant information found. Please visit the links manually for more details.")
    else:
        print_results(results, query)

    # Process the filename for saving results
    filename = re.sub(r'[<>:"/\\|?*]', '_', query.lower().replace(' ', '-'))
    filename = filename.rstrip('.')

    # Save the results to a text file
    with open(f'{filename}.txt', 'w', encoding='utf-8') as f:
        for title, summary, text in results:
            f.write(f'Title: {title}\n')
            f.write(f'Summary: {summary}\n')
            f.write(f'Text: {text[:1000]}\n\n')

def print_results(results, query):
    for title, summary, _ in results:
        print(f"Title: {title}")
        print(f"Summary: {summary}\n")

# Main loop
while True:
    # Get the search query from the user
    query = input('Enter a Wikipedia link or search query (type "done", "quit", or "exit" to stop): ')
    
    # Check if the user wants to quit
    if query.lower() in ['done', 'quit', 'exit']:
        print("Exiting...")
        break
    
    # Call the search function
    search(query)

# Chatgpt used for side notes and what is what, also make sure you do imports on 3.12 python and select that intereperter [i can't spell bruh] press 'ctrl + `' for terminal
