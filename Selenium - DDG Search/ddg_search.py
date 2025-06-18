# df 
import pandas as pd

# time
import time
import random


# selenium
from selenium import webdriver
import urllib

# bs4
from bs4 import BeautifulSoup



count = 1

# Setup Driver
def setup_driver():
        options = webdriver.ChromeOptions()
        #options.add_argument('--headless')
        #options.add_argument('--disable-gpu')
        #options.add_argument('--no-sandbox')
        #options.add_argument('--disable-dev-shm-usage')
        #options.add_argument('--disable-blink-features=AutomationControlled')
        #options.add_experimental_option("excludeSwitches", ["enable-automation"])
        #options.add_experimental_option('useAutomationExtension', False)
        
        #user_agents = [
        #    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        #    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/91.0.864.48',
        #    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15',
        #    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        #]
        #options.add_argument(f'user-agent={random.choice(user_agents)}')
        return webdriver.Chrome(options=options)


# Setup the Search
def search_duckduckgo(driver, search_query, research_type, max_results=10):


    global count
    count += 1

    if (count%100) == 0:
        print(count)

    #url = f"https://html.duckduckgo.com/html/?q={query}&kz=1&l=us-en" # old
    if research_type == 'url':
        query = f"{search_query}"
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}&b=&kp=-1&kl=us-en&df="
    elif research_type == 'hq_address':
        query = f"{search_query}"
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}&b=&kp=-1&kl=us-en&df="

    elif research_type == 'hq_address_domain':
        query = f"{search_query}"
        encoded_query = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}&b=&kp=-1&kl=us-en&df="

    print(url)
        

    
    # Add a short delay to avoid rate-limiting
    time.sleep(random.uniform(1.0, 2.0))  

    # Send request
    #response = requests.get(url, headers=headers)
    driver.get(url)
    time.sleep(2)
    

    # Check if request was successful
    #if response.status_code != 200:
    #    print(f"Error: Received status code {response.status_code}")
    #    return pd.DataFrame()  # Return empty DataFrame on failure

    response = driver.page_source
    # Parse the HTML response
    soup = BeautifulSoup(response, "html.parser")

    # Extract search results
    results = []
    for result in soup.select(".result")[:max_results]:  # Select first `max_results`
        title_tag = result.select_one(".result__title")
        link_tag = result.select_one(".result__url")
        content_tag = result.select_one(".result__snippet")

        if title_tag and link_tag and content_tag:
            title = title_tag.get_text(" ", strip=True)  # Ensure spaces between elements
            link = link_tag.get_text(strip=True)  # Get visible link text
            content = content_tag.get_text(" ", strip=True)  # Ensure proper spacing

            results.append({"title": title, "href": f"https://{link}", "body": content})


    # Convert results to DataFrame
    df = pd.DataFrame(results)

    return df



# Set up Selenium WebDriver (ensure chromedriver is installed)
def scrape_webpage(driver, url):
    
    try:
        print(url)
        driver.get(url)
        time.sleep(3)  # Wait for the page to load (adjust as needed)
        
        # Extract the page source
        page_source = driver.page_source
        
        # Use BeautifulSoup to parse and clean the text
        soup = BeautifulSoup(page_source, "html.parser")
        text_content = " ".join([p.get_text() for p in soup.find_all("p")])
        
        return text_content[:4000]  # Limit to first 4000 characters (token limit)
    
    except Exception as e:
        print(f"Error loading page: {e}")
        return None
