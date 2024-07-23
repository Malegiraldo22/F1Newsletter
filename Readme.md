# F1 Newsletter with CrewAI and Gemini

## Overview
Welcome to **F1 Newsletter with CrewAI and Gemini**. This project uses CrewAI and Gemini to automize the creation of a F1 Newsletter with the top 5 news in the last 24 hours.

## Features
* Multi-agent crew to search news, analyze them, and compile the newsletter
* Integration with Gemini to power the agents and generate content based on the news found
* Creation of a Newsletter in markdown format, ready to be sent through email or published online

## Getting Started
### Prerequisites
Before you begin, ensure you have the following:
* Python 3.12
* CrewAI 0.32
* Langchain 0.1.20
* Langchain Google GenAI 1.0.6
* Access to Gemini or another LLM API
* [Serper.dev](https://serper.dev/) API key
* Environment variables set up for your API credentials

### Installation

#### 1. Clone the repository
```sh
git clone https://github.com/Malegiraldo22/F1Newsletter
cd F1Newsletter
```
#### 2. Install dependencies
```sh
pip install -r requirements.txt
```

#### 3. Set up environment variables
Create a `.env` file in the project directory with the following content:
```
GEMINI_KEY = your_gemini_key
SERPER_API_KEY = your_serper_api_key
```

#### Usage
Run the app:
```
python main.py
```

## Detailed Description

### Agents
The `agents.py` file contains the agents needed to run the crew

#### News researcher
This agent is in charge of searching the latest F1 news. It uses tools to search on the internet, check the [Tools](###Tools) section for more info
```python
def news_researcher(self):
        return Agent(
           role='News researcher',
           goal='Research news about F1',
           backstory='Journalist with experience in reseach news on websearch engines',
           tools=[SearchTool.search_internet, SearchTool.search_news],
           verbose=True,
           llm=self.Gemini,
           max_rpm=2 
        )
```
**Note**: The max_rpm attribute controls the number of requests per minute that an agent can perform to avoid rate limits. It's set to 2 rpm due to Gemini's free tier limitations. This can be removed or modified if you are using a pay-as-you-go plan or another LLM with a higher rpm limit.

#### News Scraper
This agent takes the news found by the researcher and scraps the news content for each one. If it can't scrape the news, it moves to the next link.

```python
def news_scraper(self):
        return Agent(
           role='News Scraper',
           goal='Use Scrap tools to extract the news content from the links passed by the news researcher and resume them',
           backstory='Journalist with experience in scraping news from websites',
           tools=[SearchTool.scrape_website],
           verbose=True,
           llm=self.Gemini,
           max_rpm=2 
        )
```

#### News Analyzer
Analyzes each news item found and summarizes each one. Also redacts the newsletter with the information found and scraped. In a hierarchical run, it checks if the news found by the researcher are part of the F1 context and how interesting each one is. If it isn't part of the context or interesting, it rejects the news and makes the researcher search for more news.

```python
def news_analyzer(self):
        return Agent(
            role='News analyzer',
            goal='Read the news found, analyze them improve the resume making them accessible and engaging for our audience',
            backstory='Journalist with broad experience in F1 in both technical and sport analysis',
            verbose=True,
            llm=self.Gemini,
            max_rpm=2
        )
```

#### Newsletter compiler
This agent compiles the newsletter with the analyzer output

```python
def newsletter_compiler(self):
        return Agent(
            role='Newsletter compiler',
            goal='Compile the reviewed and rewrited news in a final newsletter format',
            backstory="Editor with experience in compiling newsletters in a meticously and concise format ensuring a coherent and visually presentation that captivates the readers",
            verbose=True,
            llm=self.Gemini,
            max_rpm=2
        )
```
### Tools
Some agents use tools to either search on the internet or scrap websites

#### Search on internet
This tool is used by the crew to search on the internet about a given topic and return relevant results. It uses the Serper.dev API to make the search, returning a list of the top 5 results with the title, link, date if available, and a snippet.

```python
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
```
**Note**: The amount of results can be changed to include more results

#### Search news
This tool searches for news on Google News using the Serper.dev API. It works similarly to the Search on Internet tool.
```python
@tool("Search news in the internet")
    def search_news(query):
        """
        Useful to news on the internet in the last 24 hours
        """
        print("Searching the internet...")
        top_result_to_return = 5
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
```

#### Scrape data from website
This tool uses CrewAI ScrapeWebsiteTool to scrape data from a website
```python
@tool("Scrape data from website")
    def scrape_website(url):
        """
        Useful to scrape data from a website in case needed
        """
        tool = ScrapeWebsiteTool(url)
        text = tool.run()
        return text
```

#### Save markdown
Saves the final output in a markdown file
```python
def save_markdown(task_output):
    # Get today's date in the format YYYY-MM-DD
    today_date = datetime.now().strftime('%Y-%m-%d')
    # Set the filename with today's date
    filename = f"F1 News {today_date}.md"
    output = str(task_output.raw_output)
    # Write the task output to the markdown file
    with open(filename, 'w') as file:
        file.write(output)
    print(f"File saved as {filename}")
```

### Tasks
The agents need tasks to run, these are defined like this

#### Search news
Fetchs the most recent news and stores them in a list
```python
def search_news(self, agent):
        return Task(
            description=f"Fetch top F1 news published in the last 24 hours. It can be news about teams, tracks, drivers, events and everything related with F1. The current date is {datetime.now()}. {self.__tip_section()}",
            agent=agent,
            async_execution=False,
            expected_output=dedent("""\
                            A list of top F1 news stories titles, URLs and a summary for each story in the last 24 to 48 hours.
                            Example output:
                            [
                                {'title': 'Adrian Newey signs for Ferrari',
                                 'url':'https://example.com/story',
                                }
                            ]
                            """,)
        )
```

#### Scrape news
Handles the scraping of each website passed by the news research and stores the content of each website in the list
```python
def scrape_news(self, agent, context):
        return Task(
            description=f'Use the list of top F1 news stories titles, scrap each link provided and paste the news content. If the content is not available or cannot be scraped, delete it from the list and move to the next link',
            agent=agent,
            async_execution=False,
            context=context,
            expected_output=dedent("""\
                            A list of top F1 news stories titles, URLs, summary and news content for each story in the last 24 hours.
                            Example output:
                            [
                                {'title': 'Adrian Newey signs for Ferrari',
                                 'content':'Former RedBull car designer signs for Ferrari from 2025 to 2027...'
                                },
                                {{...}}
                            ]
                            """)
        )
```

#### Analyze news
Takes the content from each news and writes a resume divided in three sections finalizing with and analysis on it's impact in the F1 context
```python
def analyze_news(self, agent, context):
        return Task(
            description=f'Use the news list and write a resume and analysis of each news on how impacts the F1 environment. {self.__tip_section()}',
            agent=agent,
            async_execution=False,
            context=context,
            expected_output=dedent("""\
            An analysis of each news story, including a rundonw, detailed bulletpoints, and an analysis section in the F1 spectrum.
            Example output:
            [
                {'title': 'Adrian Newey signs for Ferrari',
                 'content':'Former RedBull car designer signs for Ferrari from 2025 to 2027...',
                 'The rundown':'Adrian Newey signs for Ferrari from 2025...',
                 'The details':'Former redbull chief car and aerodynamic designer...',
                 'The Analysis':'The biggest team change besides drivers would make a huge change...'
                },
                {{...}}
            ]
            """)
        )
```

#### Redact news
Evaluates the redaction of the resume and makes changes if necessary to make them more engaging. Also checks if there are at least 5 articles and starts to make the markdown file
```python
def redact_news(self, agent, context):
        return Task(
            description=f'Evaluate the redaction and format of each news, write it again if necessary. {self.__tip_section()}',
            agent=agent,
            async_execution=False,
            context=context,
            expected_output=dedent("""\
            A markdown formatted newsletter with clear and improved redaction. including a rundown, detailed bulletpoints, and an analysis section in the F1 spectrum. 
            There should be at least 5 articles, each following the proper format.
            Example output:
            '##Adrian Newey signs for Ferrari\n
            ** The rundown:
            ** Adrian Newey signs for Ferrari from 2025...\n
            **The Details:
            ** Former redbull chief car and aerodynamic designer...\n
            **The Analysis:
            ** The biggest team change besides drivers would make a huge change...'
            """)
        )
```

#### Compile news
Takes the markdown and finalizes it making sure that it's in the right format
```python
def compile_news(self, agent, context, callback_func):
        return Task(
            description=f'Finish and format the newsletter in a markdown file following the desired output, using the information found and save it using the callback function. DO NOT GENERATE CONTENT, ONLY ORGANIZE THE INFORMATION IN THE DESIRED OUTPUT. {self.__tip_section()}',
            agent=agent,
            async_execution=False,
            context=context,
            expected_output=dedent(f"""\
                A complete newsletter saved in markdown format, with consistency and layout.
                Make sure that all fields are complete
                Example output:
                # Top Stories in F1 today {date.today()}\n
                - Adrian Newey signs for Ferrari\n
                - Lawrance Stroll fires Lance Stroll, promises to bring a better driver to Aston Martin\n\n
                ##Adrian Newey signs for Ferrari\n
                ** The Rundown:...\n
                ** The Details:...\n
                ** The Analysis:...\n
                ## Lawrance Stroll fires Lance Stroll, promises to bring a better driver to Aston Martin\n\n
                ** The Rundown:...\n
                ** The Details:...\n
                ** The Analysis:...\n
                """),
            callback=callback_func
        )
```

### Main
The main script `main.py` orchestrates the agents and the overall workflow

#### LLM model configuration
Depending on the model you'll need to import a different library to handle your LLM model check more [here](https://docs.crewai.com/how-to/LLM-Connections/)

```python
Gemini = ChatGoogleGenerativeAI(
    model='gemini-1.5-pro',
    verbose=True,
    google_api_key=os.environ['GEMINI_KEY']
)
```
#### Initializing agents and tasks
```python
agents = NewsAgents()
tasks = NewsletterTasks()

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
```
#### Initializing crew and run it

```python
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
```

## Limitations
* Gemini limits the amount of rpm to 2 on their free tier. Also the number of tokens generated by rpm and daily are a limit. Therefore there's an increase in the amount of time that it takes to run the tasks
* On another LLM it's possible to run them faster but it could lead to a high usage price unless you are running a local LLM using Ollama

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request with your changes.

## Contact

For any questions or comments, please open an issue on GitHub or contact me directly at magiraldo2224@gmail.com