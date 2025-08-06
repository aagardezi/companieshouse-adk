from companieshouse import CompaniesHouseClient
import companies_house_agent.tools.helpercode as helpercode

PROJECT_ID = helpercode.get_project_id()

chclient = CompaniesHouseClient(api_key=helpercode.access_secret_version(PROJECT_ID, "CompaniesHouseAPIKey"))

def search_companies(search_query:str):
    """
    Searches for companies in the Companies House database based on the given search query.

    Args:
        search_query (str): The search query. Usually a name of a company

    Returns:
        A dictionary containing the search results.
    """
    return chclient.search_companies(search_query)

def get_company_profile(company_number:str):
    """
    Gets the profile of a company in the Companies House database based on the given company number.

    Args:
        company_number: The company number of the company. Usaully returned in the company search response

    Returns:
        A dictionary containing the company profile.
    """
    return chclient.get_company_profile(company_number)

def get_company_officers(company_number:str):
    """
    Gets the company officers from the Companies House database based on the given company number.

    Args:
        company_number: The company number.

    Returns:
        A dictionary containing the company officers details.
    """
    return chclient.get_company_officers(company_number)

# def get_company_filing_history(company_number):
#     """
#     Gets the company filing history .

#     Args:
#         company_number: The company number.

#     Returns:
#         A dictionary containing the filing history.
#     """
#     # company = chclient.get_company_profile(company_number)

#     # return chclient.get_company_filing_history(filing_history_url)