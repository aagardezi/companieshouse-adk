from companieshouse import CompaniesHouseClient
from zoneinfo import ZoneInfo
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.tools import agent_tool
from google.adk.tools import google_search
from .tools.companieshouse_tools import search_companies, get_company_profile, get_company_officers, get_company_filing_history

search_companies_agent = Agent(
    name="search_companies_agent",
    model="gemini-2.5-flash",
    description=(
        "You are an agent helping to analyse companies and search in the companies house database"
    ),
    instruction=(
        "You are an agent looking searching for companies in the companies house database"
        "Use the search_companies tool to get a list of companies from a company name"
        "the company number will be needed for subsequent sub agents"
        "if you retrieive multiple companies, make an assumption about what is the most likely symbol"
        "return the company number and full name in the response"
        "If there is no clear company in the reuslt ask the user to choose the company"
    ),
    tools=[search_companies],
    output_key="search_companies_result"
)

get_company_profile_agent = Agent(
    name="get_company_profile_agent",
    model="gemini-2.5-flash",
    description=(
        "You are an agent helping to analyse companies get company details from the companies house database"
    ),
    instruction=(
        "You are an agent for getting company details in the companies house database"
        "Use the get_company_profile tool to get the details of the company from a company number"
        "the company details including officer details and filing_history_url will be needed for subsequent sub agents"
        "return the summary of company details in the response including a list of filing_history_url"
    ),
    tools=[get_company_profile],
    output_key="company_profile_result"
)

get_company_officers_agent = Agent(
    name="get_company_officers_agent",
    model="gemini-2.5-flash",
    description=(
        "You are an agent helping to analyse companies officers from company details from the companies house database"
    ),
    instruction=(
        "You are an agent for getting company officer details in the companies house database"
        "Use the get_company_officers tool to get the details of the company officers from a company number"
        "return the summary of company officer details in the response"
    ),
    tools=[get_company_officers],
    output_key="company_officers_result"
)

get_company_filing_history_agent = Agent(
    name="get_company_filing_history_agent",
    model="gemini-2.5-flash",
    description=(
        "You are an agent helping to analyse companies filings history from company details from the companies house database"
    ),
    instruction=(
        "You are an agent for getting company filing history details in the companies house database"
        "Use the get_company_filing_history tool to get the details of the company filings history"
        "use the filings_url in the company profile retrieved by the get_company_profile_agent"
        "return the summary of company filings history details in the response"
    ),
    tools=[get_company_filing_history],
    output_key="company_filing_history_result"
)

company_report_creation_agent =  Agent(
    name="get_company_officers_agent",
    model="gemini-2.5-flash",
    description=(
        "You are an agent helping a final report on a company based on the data retrieved from the companies house database"
    ),
    instruction=(
        "You are a report creation agent for getting company details in the companies house database"
        "Input summaries: {company_profile_result}, {company_officers_result}, {company_filing_history_result}"
        "Use all the above retrieved details to create a report that can be used to assess the company"
        "Make the report detailed and have a section at the end that is a viability assessment of the company"
        "Use only the data retrieved by all the previous agents to asses the company viability"
        "Make the report comprehensive"
    )
)



root_agent = Agent(
    name="company_assessment_agent",
    model="gemini-2.5-flash",
    description=(
        "You are an agent helping analyse companies listed in the companies house database"
    ),
    instruction=(
        "You are a highly skilled companies assessment agent"
        "Use the input and the search_companies_agent to start the process"
        "use all the other agents (get_company_profile_agent, get_company_officers_agent, get_company_filing_history_agent)"
        "Once you have the data from the company use the company_report_creation_agent to create a final report"
    ),
    sub_agents=[search_companies_agent, get_company_profile_agent, get_company_officers_agent, get_company_filing_history_agent, company_report_creation_agent]
)