import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock the chclient before importing tools
from companies_house_agent.tools import helpercode
helpercode.get_project_id = MagicMock(return_value="dummy_project")
helpercode.access_secret_version = MagicMock(return_value="dummy_api_key")

# Now import the tools
try:
    from companies_house_agent.tools.companieshouse_tools import (
        search_companies,
        get_company_profile,
        get_company_officers,
        get_company_address,
        get_company_establishments,
        get_company_registers,
        get_company_exemptions,
        get_company_charges,
        get_company_insolvency,
        get_corporate_officer_disqualifications,
        get_natural_officer_disqualifications,
        get_office_appointments,
        get_company_filing_history
    )
    print("Successfully imported all tools.")
except ImportError as e:
    print(f"Failed to import tools: {e}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    print("Verification script ran successfully.")
