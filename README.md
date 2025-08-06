# Companies House Agent

This project provides a conversational agent powered by the Google ADK framework that can search for and retrieve information about companies from the UK Companies House database.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/companieshouse-adk.git
    cd companieshouse-adk
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Companies House API Key:**

    This agent requires an API key from Companies House. You can obtain one by registering a new application on the [Companies House developer portal](https://developer.companieshouse.gov.uk/).

    Once you have your API key, you need to store it in Google Cloud Secret Manager:

    a.  Enable the Secret Manager API for your Google Cloud project.
    b.  Create a new secret with the name `CompaniesHouseAPIKey`.
    c.  Add a new version to the secret with your Companies House API key as the secret value.

## Running the Agent

To start the agent, run the following command from the root of the project directory:

```bash
python -m companies_house_agent.main
```

You can then interact with the agent by typing your queries into the console.

## Testing the Agent with the ADK

The Google Agent Development Kit (ADK) provides a web-based user interface for testing and debugging your agent.

### Installing the ADK

If you haven't already, you can install the ADK using pip:

```bash
pip install google-adk
```

### Running the Web UI

To start the ADK web UI, run the following command from the root of the project directory:

```bash
adk web
```

This will open a new tab in your web browser with the testing UI. From here, you can interact with your agent, create and save test cases, and inspect the agent's execution trace for debugging.

## Use Cases

This agent can be used for a variety of purposes, including:

*   **Due Diligence:** Quickly retrieve detailed information about a company, including its officers, filing history, and current status.
*   **Automated Company Monitoring:** The agent could be extended to monitor a list of companies and provide notifications of any new filings or changes in company status.
*   **Market Research:** Analyze trends in company formation and dissolution in specific sectors or geographic areas.
*   **Lead Generation:** Identify potential business partners or customers based on their company profile and filing history.