from crewai import Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from agents import NewsAgents
from tasks import NewsletterTasks
from Tools.file_io import save_markdown
import os
from dotenv import load_dotenv
load_dotenv()

agents = NewsAgents()
tasks = NewsletterTasks()

Gemini = ChatGoogleGenerativeAI(
    model='gemini-1.5-pro',
    verbose=True,
    google_api_key=os.environ['GEMINI_KEY']
)

Llama = ChatGroq(
    model_name='llama3-70b-8192',
    api_key = os.environ['GROQ_KEY'],
)

#Agents
news_researcher = agents.news_researcher()
news_scraper = agents.news_scraper()
news_analyzer = agents.news_analyzer()
newsletter_compiler = agents.newsletter_compiler()

#Tasks
search_news = tasks.search_news(news_researcher)
scrape_news = tasks.scrape_news(news_scraper, [search_news])
analyze_news = tasks.analyze_news(news_analyzer, [scrape_news])
redact_news = tasks.redact_news(news_analyzer, [analyze_news])
compile_news = tasks.compile_news(newsletter_compiler, [redact_news], save_markdown)

crew = Crew(
    agents=[news_researcher, news_scraper, news_analyzer, newsletter_compiler],
    tasks=[search_news, scrape_news, analyze_news, redact_news, compile_news],
    process=Process.hierarchical,
    manager_llm=Gemini,
    verbose=1
)

results = crew.kickoff()

print("Crew results")
print(results)