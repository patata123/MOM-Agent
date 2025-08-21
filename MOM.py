import json
import os
from crewai import Agent, Task, Crew
from crewai_tools import FirecrawlScrapeWebsiteTool
from dotenv import load_dotenv
from crewai_tools import ScrapeElementFromWebsiteTool # Retire this tool as it does not seemed to fit our usecase now 
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from crewai.tools import tool  # this is the compatible @tool decorator
import pandas as pd
import requests
from firecrawl.firecrawl import FirecrawlApp


load_dotenv('.env')

# -----------------------
# Tools
# -----------------------

@tool
def download_file(url: str, filename: str = None) -> str:
    """Download a file from a URL and save it to the 'downloads' folder."""
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    local_filename = filename or url.split('/')[-1]
    path = os.path.join('downloads', local_filename)

    response = requests.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)
    
    return f"Downloaded to {path}"

@tool("Custom Firecrawl Scraper")
def firecrawl_scrape(url: str) -> str:
    """Scrapes content from a URL using the Firecrawl API and returns markdown output.
    """
    try:
        if not url:
            return "Missing 'url' parameter."

        app = FirecrawlApp()
        result = app.scrape_url(url, formats=["markdown"])
        return str(result)

    except Exception as e:
        return f"Scraping failed: {str(e)}"
    
@tool
def select_statistical_table_url() -> list:
    """Selects the most relevant Statistical Table URL from output.json based on the user query."""
    with open('output.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    tables = [
        page for page in data['Pages']
        if "Statistical Table" in page.get("Title", "")
    ]

    return tables

# -----------------------
# Agents
# -----------------------

web_scraper_agent = Agent(
    role="Web Scraper",
    goal="Extract specific information from websites",
    backstory="An expert in web scraping who can extract targeted content from web pages.",
    tools=[firecrawl_scrape],
    verbose=True,
)

markdown_selector_agent = Agent(
    role="Markdown Selector",
    goal="Given a markdown table and a user query, find the most appropriate CSV file link to download",
    backstory="You analyze markdown tables and extract the XLSX file that best matches the user's data needs.",
    tools=[],
    verbose=True,
)

download_agent = Agent(
    role="Downloader",
    goal="Download and save a given CSV or Excel file locally",
    backstory="You are in charge of file handling and downloading from the web.",
    tools=[download_file],
    verbose=True,
)

stat_table_selector_agent = Agent(
    role="Statistical Table Selector",
    goal="Select the most relevant Statistical Table URL from the tool's output based on user query",
    backstory="You analyze the user's query and choose the best matching Statistical Table page.",
    tools=[select_statistical_table_url],
    verbose=True,
)

# -----------------------
# Tasks
# -----------------------

stat_table_selector_task = Task(
    description="Given the user query '{query}', select the most relevant Statistical Table URL from output.json.",
    expected_output="The best matching Statistical Table URL.",
    agent=stat_table_selector_agent,
)

scrape_task = Task(
    description="Use the web_scraper_agent tool to extract the selected URL in markdown format",
    expected_output="A markdown table containing the dataset title, dataset csv/xlsx link.",
    agent=web_scraper_agent,
    context=[stat_table_selector_task],
)

markdown_selector_task = Task(
    description="Given the markdown table extracted from the MOM site and a user query '{query}', identify the most appropriate XLSX link to download.",
    expected_output="The best matching XLSX URL delimited by <URL>",
    agent=markdown_selector_agent,
    context=[scrape_task]
)

download_task = Task(
    description="Use the download_file tool to save the best matching XLSX selected by Markdown Selector agent",
    expected_output="downloaded files in directory",
    agent=download_agent,
    context=[markdown_selector_task]
)

# -----------------------
# Crew
# -----------------------

crew = Crew(
    agents=[stat_table_selector_agent, web_scraper_agent, markdown_selector_agent, download_agent],
    tasks=[stat_table_selector_task, scrape_task, markdown_selector_task, download_task]
)

# # For Unemployment downloads
# result = crew.kickoff(inputs={
#     "url": "https://stats.mom.gov.sg/Pages/UnemploymentTimeSeries.aspx",
#     "query": "unemployment by industry"
# })



result = crew.kickoff(inputs={
    "query": "Retrenchment by residential status"
})