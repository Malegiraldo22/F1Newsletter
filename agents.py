from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from Tools.search_tool import SearchTool
import os
from dotenv import load_dotenv
load_dotenv()

class NewsAgents():

    def __init__(self):
        self.Gemini = ChatGoogleGenerativeAI(
            model='gemini-1.5-pro',
            verbose=True,
            google_api_key=os.environ['GEMINI_KEY']
        )

        self.Llama = ChatGroq(
            model_name='llama3-70b-8192',
            api_key = os.environ['GROQ_KEY'],
        )

    def news_researcher(self):
        return Agent(
           role='News researcher',
           goal='Fetch news about F1 published in the last 24 hours',
           backstory='Journalist with experience in reseach news on websearch engines',
           tools=[SearchTool.search_internet, SearchTool.search_news, SearchTool.scrape_website],
           verbose=True,
           llm=self.Llama,
           max_rpm=20
        )
    
    def news_scraper(self):
        return Agent(
           role='News Scraper',
           goal='Use Scrap tools to extract the news content from the links passed by the news researcher and resume them',
           backstory='Journalist with experience in scraping news from websites',
           tools=[SearchTool.scrape_website],
           verbose=True,
           llm=self.Llama,
           max_rpm=20
        )
    
    def news_analyzer(self):
        return Agent(
            role='News analyzer',
            goal='Read the news found, analyze them improve the resume making them accessible and engaging for our audience',
            backstory='Journalist with broad experience in F1 in both technical and sport analysis',
            verbose=True,
            llm=self.Llama,
            max_rpm=20
        )

    def newsletter_compiler(self):
        return Agent(
            role='Newsletter compiler',
            goal='Compile the reviewed and rewrited news in a final newsletter format',
            backstory="Editor with experience in compiling newsletters in a meticously and concise format ensuring a coherent and visually presentation that captivates the readers",
            verbose=True,
            llm=self.Llama,
            max_rpm=20
        )