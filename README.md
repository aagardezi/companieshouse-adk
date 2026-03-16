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

## Running Evaluations

This project includes a suite of automated evaluations to verify the agent's performance and tool usage. These evaluations are built using the ADK evaluation framework.

### Prerequisites

Ensure you have installed the dependencies:
```bash
pip install -r requirements.txt
```

### Running the Evals

You can run evaluations using either the `adk eval` command or the provided script.

#### Option 1: Running with `adk eval` (Recommended)

The `adk eval` command provides more configuration options and detailed output. From the root of the project directory, run:

```bash
adk eval --config_file_path companyagenttest/evals/test_config.json companies_house_agent companyagenttest/evals/companies_house_agent.test.json
```

**Note**: You must provide the `--config_file_path` to ensure the correct evaluation criteria are applied. You can also add `--print_detailed_results` to see detailed scoring information for each test case.

#### Option 2: Running with `run_evals.py` Script

To run the evaluations using the script, execute it from the `companyagenttest/evals` directory:

```bash
cd companyagenttest/evals
python3.12 run_evals.py
```

This will run the evaluation cases defined in `companies_house_agent.test.json` and display the results. Detailed output, including any failures, will be saved to `eval_output.txt`.

### Evaluation Dataset

The evaluation dataset (`companies_house_agent.test.json`) contains test cases designed to verify:
-   **UK Company Focus**: The dataset exclusively tests with verified UK companies (e.g., Google UK Limited, Barclays Capital Securities Limited, The Co-mission Churches Trust) to align with Companies House data.
-   **Tool Trajectory**: Verifies that the agent calls the correct tools in the expected sequence.
-   **Response Accuracy**: Verifies that the agent provides accurate and concise answers based on the retrieved data.

## Recent Updates (v0.4)

The agent has been updated to use version 0.4 of the `companies-house-api-lib`. This update introduces improved filing history capabilities:
*   **Filing History Listing**: Retrieve a list of filings for a company.
*   **Filing Details**: Fetch individual filing details (including annotations and detailed descriptions) based on transaction IDs from the list.
*   **Automatic Detail Fetching**: The agent can now automatically fetch details for the most recent filings when requested, providing richer context for analysis.

## Test Prompts

You can use the following example prompts to test the agent's capabilities:

### Company Search and Profile
*   "Search for companies named 'Tesla'."
*   "Get the company profile for 'London Stock Exchange Group'."
*   "What is the company number for 'DeepMind'?"

### Officers and Appointments
*   "List the active officers for 'London Stock Exchange Group'."
*   "Who are the directors of 'DeepMind'?"
*   "Show appointments for officer 'Lisa Margaret Condron'."

### Filing History, Charges, and Insolvency
*   "Get the filing history for 'London Stock Exchange Group'."
*   "What are the 3 most recent filings for company 05369106?"
*   "Show me the details for the most recent filing of 'DeepMind'."
*   "Check if company 07496944 has any charges."
*   "Does company 07496944 have insolvency records?"

### Comprehensive Analysis
*   "Perform a viability assessment for 'London Stock Exchange Group' based on its profile, officers, and filing history."
*   "Analyze the credit risk for 'Tesla' based on available information."
*   "Create a comprehensive report on 'London Stock Exchange Group'."

## Use Cases

This agent can be used for a variety of purposes, including:

*   **Due Diligence:** Quickly retrieve detailed information about a company, including its officers, filing history, and current status.
*   **Automated Company Monitoring:** The agent could be extended to monitor a list of companies and provide notifications of any new filings or changes in company status.
*   **Market Research:** Analyze trends in company formation and dissolution in specific sectors or geographic areas.
*   **Lead Generation:** Identify potential business partners or customers based on their company profile and filing history.