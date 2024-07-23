import json
import os
import requests
from langchain.tools import tool
from crewai_tools import ScrapeWebsiteTool, SeleniumScrapingTool


class SearchTool():

    @tool("Search on internet")
    def search_internet(query):
        """
        Useful to search the internet about a given
        topic and return relevant results
        """
        print("Searching the internet...")
        top_result_to_return = 5
        url = "https://google.serper.dev/search"
        payload = json.dumps(
            {"q": query, "gl":"co"}
        )
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # check if there is an organic key
        if 'organic' not in response.json():
            return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
        else:
            results = response.json()['organic']
            string = []
            for result in results[:top_result_to_return]:
                try:
                    # Attempt to extract the date
                    date = result.get('date', 'Date not available')
                    string.append('\n'.join([
                        f"Title: {result['title']}",
                        f"Link: {result['link']}",
                        f"Date: {date}",  # Include the date in the output
                        f"Snippet: {result['snippet']}",
                        "\n-----------------"
                    ]))
                except KeyError:
                    next

            return '\n'.join(string)
        
    @tool("Search news in the internet")
    def search_news(query):
        """
        Useful to news on the internet in the last 24 hours
        """
        print("Searching the internet...")
        top_result_to_return = 10
        url = "https://google.serper.dev/news"
        payload = json.dumps(
            {"q": query, "tbs": "qdr:d"}
        )
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # check if there is an organic key
        if 'news' not in response.json():
            return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
        else:
            results = response.json()['news']
            string = []
            for result in results[:top_result_to_return]:
                try:
                    # Attempt to extract the date
                    date = result.get('date', 'Date not available')
                    string.append('\n'.join([
                        f"Title: {result['title']}",
                        f"Link: {result['link']}",
                        f"Date: {date}",  # Include the date in the output
                        f"Snippet: {result['snippet']}",
                        "\n-----------------"
                    ]))
                except KeyError:
                    next

            return '\n'.join(string)

        
        
    @tool("Scrape data from website")
    def scrape_website(url):
        """
        Useful to scrape data from a website in case needed
        """
        tool = ScrapeWebsiteTool(url)
        text = tool.run()
        return text
    
    @tool("Scrape data from websites using selenium")
    def scrape_website_selenium(url):
        """
        Useful to extract data from a website with selenium when
        the scrape website tool hasn't worked well
        """
        tool = SeleniumScrapingTool(url=url, wait_time=5)
        text = tool.run()
        return text
