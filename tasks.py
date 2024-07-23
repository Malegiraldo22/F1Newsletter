from datetime import datetime, date
from crewai import Task
from textwrap import dedent

class NewsletterTasks():

    def __tip_section(self):
        return "If you realize the best job possible, I'll give you a $100.000 dollar bonus"

    def search_news(self, agent):
        return Task(
            description=f"Fetch top F1 news published in the last 24 hours. Provide a list containing the title and url of each news. The current date is {datetime.now()}. {self.__tip_section()}",
            agent=agent,
            async_execution=False,
            expected_output=dedent("""\
                            Top F1 news stories titles and URLs for each story in the last 24 hours, in the next format (OBLIGATORY):
                            [
                                {'title': 'Adrian Newey signs for Ferrari',
                                 'url':'https://example.com/story'
                                }
                            ]
                            """,)
        )
    
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
    
    def analyze_news(self, agent, context):
        return Task(
            description=f'Use the news content and write a resume and analysis of each news on how impacts the F1 environment. {self.__tip_section()}',
            agent=agent,
            async_execution=False,
            context=context,
            expected_output=dedent("""\
            An analysis of each news story, including a rundown, detailed bulletpoints, and an analysis section in the F1 spectrum.
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
    
    def redact_news(self, agent, context):
        return Task(
            description=f'Evaluate the redaction and format of each news, write it again making the news engaging and interesting. {self.__tip_section()}',
            agent=agent,
            async_execution=False,
            context=context,
            expected_output=dedent("""\
            A markdown formatted newsletter with clear and improved redaction. including a rundown, detailed bulletpoints, and an analysis section in the F1 spectrum. 
            There should be at least 5 articles, each following the proper format.
            Example output:
            '##Adrian Newey signs for Ferrari\n
            ** Adrian Newey signs for Ferrari from 2025...\n
            ** Former redbull chief car and aerodynamic designer...\n
            ** The biggest team change besides drivers would make a huge change...'
            ## Lawrance Stroll fires Lance Stroll, promises to bring a better driver to Aston Martin\n\n
            ...
            """)
        )
    
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
                ...
                ## Lawrance Stroll fires Lance Stroll, promises to bring a better driver to Aston Martin\n\n
                ...
                """),
            callback=callback_func
        )