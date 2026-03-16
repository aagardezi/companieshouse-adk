import os
import sys
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import agent_tool
from google.adk.tools import google_search
from .tools.companieshouse_tools import (
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
    get_company_filing_history,
    get_company_filing_detail
)
from .config import config


from google.adk.events.event import Event
from google.adk.events.event_actions import EventActions
from google.adk.utils.context_utils import Aclosing

class SubAgentEvent(Event):
    """Event wrapper that hides final response status.
    
    This is used to prevent parent agents from breaking their execution loop
    prematurely when a subagent finishes.
    """
    def is_final_response(self) -> bool:
        return False

# Workaround Patches
original_seq_run_async_impl = SequentialAgent._run_async_impl

async def workaround_seq_run_async_impl(self, ctx):
    if not self.sub_agents:
        return

    from google.adk.agents.sequential_agent import SequentialAgentState
    agent_state = self._load_agent_state(ctx, SequentialAgentState)
    start_index = self._get_start_index(agent_state)

    pause_invocation = False
    resuming_sub_agent = agent_state is not None
    
    for i in range(start_index, len(self.sub_agents)):
        sub_agent = self.sub_agents[i]
        if not resuming_sub_agent:
            if ctx.is_resumable:
                agent_state = SequentialAgentState(current_sub_agent=sub_agent.name)
                ctx.set_agent_state(self.name, agent_state=agent_state)
                yield self._create_agent_state_event(ctx)

        sub_ctx = ctx.model_copy(update={"agent": sub_agent})
        async with Aclosing(sub_agent.run_async(sub_ctx)) as agen:
            async for event in agen:
                # Wrap event if NOT the last subagent
                if i < len(self.sub_agents) - 1:
                    if event.author != self.name:
                        wrapped_event = SubAgentEvent(
                            author=event.author,
                            content=event.content,
                            timestamp=event.timestamp,
                            actions=event.actions,
                            invocation_id=event.invocation_id,
                            # id=event.id,
                            branch=event.branch
                        )
                        yield wrapped_event
                    else:
                        yield event
                else:
                    # Last subagent, yield unwrapped
                    yield event
                
                if ctx.should_pause_invocation(event):
                    pause_invocation = True

        if pause_invocation:
            return

        resuming_sub_agent = False

    if ctx.is_resumable:
        ctx.set_agent_state(self.name, end_of_agent=True)
        yield self._create_agent_state_event(ctx)

SequentialAgent._run_async_impl = workaround_seq_run_async_impl

original_parallel_run_async_impl = ParallelAgent._run_async_impl

async def workaround_parallel_run_async_impl(self, ctx):
    if not self.sub_agents:
        return

    from google.adk.agents.base_agent import BaseAgentState
    agent_state = self._load_agent_state(ctx, BaseAgentState)
    if ctx.is_resumable and agent_state is None:
        ctx.set_agent_state(self.name, agent_state=BaseAgentState())
        yield self._create_agent_state_event(ctx)

    agent_runs = []
    from google.adk.agents.parallel_agent import _create_branch_ctx_for_sub_agent
    for sub_agent in self.sub_agents:
        sub_agent_ctx = _create_branch_ctx_for_sub_agent(self, sub_agent, ctx)
        sub_agent_ctx.agent = sub_agent
        if not sub_agent_ctx.end_of_agents.get(sub_agent.name):
            agent_runs.append(sub_agent.run_async(sub_agent_ctx))

    pause_invocation = False
    try:
        from google.adk.agents.parallel_agent import _merge_agent_run, _merge_agent_run_pre_3_11
        merge_func = _merge_agent_run if sys.version_info >= (3, 11) else _merge_agent_run_pre_3_11
        
        last_event = None
        accumulated_state_delta = {}
        async with Aclosing(merge_func(agent_runs)) as agen:
            async for event in agen:
                last_event = event
                
                # Accumulate state delta
                if event.actions and event.actions.state_delta:
                    accumulated_state_delta.update(event.actions.state_delta)
                
                # Always wrap subagent events in ParallelAgent
                if event.author != self.name:
                    wrapped_event = SubAgentEvent(
                        author=event.author,
                        content=event.content,
                        timestamp=event.timestamp,
                        actions=event.actions,
                        invocation_id=event.invocation_id,
                        # id=event.id,
                        branch=event.branch
                    )
                    yield wrapped_event
                else:
                    yield event
                
                if ctx.should_pause_invocation(event):
                    pause_invocation = True

        if pause_invocation:
            return

        # Yield a final response event if last_event was final
        if last_event and last_event.is_final_response():
            dump = last_event.model_dump()
            dump['id'] = '' # Force new ID
            final_event = Event(**dump)
            if final_event.actions:
                final_event.actions.state_delta = accumulated_state_delta
            else:
                final_event.actions = EventActions(state_delta=accumulated_state_delta)
            final_event.author = self.name
            yield final_event

        if ctx.is_resumable and all(
            ctx.end_of_agents.get(sub_agent.name) for sub_agent in self.sub_agents
        ):
            ctx.set_agent_state(self.name, end_of_agent=True)
            yield self._create_agent_state_event(ctx)

    finally:
        for sub_agent_run in agent_runs:
            await sub_agent_run.aclose()

ParallelAgent._run_async_impl = workaround_parallel_run_async_impl


search_companies_agent = Agent(
    name="search_companies_agent",
    # model="gemini-2.5-flash",
    model=config.gemini_model,
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

search_companies_google_agent = Agent(
    name="search_companies_google_agent",
    # model="gemini-2.5-flash",
    model=config.gemini_model,
    description=(
        "You are an agent helping to analyse companies and search in google search"
    ),
    instruction=(
        "You are an agent looking searching for companies in the companies house database"
        "Use the google_search tool to details of a company"
        "if you retrieive multiple companies, make an assumption about what is the most likely symbol"
        "return a full summary of the company include employee numbers etc"
    ),
    tools=[google_search],
    output_key="search_companies_google_result"
)

get_company_profile_agent = Agent(
    name="get_company_profile_agent",
    # model="gemini-2.5-flash",
    model=config.gemini_model,
    description=(
        "You are an agent helping to analyse companies get company details from the companies house database"
    ),
    instruction=(
        "You are an agent for getting company details in the companies house database"
        "Use the get_company_profile tool to get the details of the company from the company number"
        "The company number should be available in the conversation history or context."
        "the company details including officer details and filing_history_url will be needed for subsequent sub agents"
        "return the detailed summary of company details in the response including a list of filing_history_url"
    ),
    tools=[get_company_profile],
    output_key="company_profile_result"
)

get_company_officers_agent = Agent(
    name="get_company_officers_agent",
    # model="gemini-2.5-flash",
    model=config.gemini_model,
    description=(
        "You are an agent helping to analyse companies officers from company details from the companies house database"
    ),
    instruction=(
        "You are an agent for getting company officer details in the companies house database"
        "Use the get_company_officers tool to get the details of the company officers from a company number"
        "The company number should be available in the conversation history or context."
        "return the summary of company officer details in the response"
    ),
    tools=[get_company_officers],
    output_key="company_officers_result"
)

credit_risk_agent = Agent(
    name="credit_risk_agent",
    # model="gemini-2.5-flash",
    model=config.gemini_model,
    description=(
        "You are an agent helping to analyse companies credit risk from company details from the companies house database"
    ),
    instruction=(
        "You are an agent for getting company credit risk details in the companies house database"
        "Use the get_company_charges and get_company_insolvency tools to get relevant data"
        "The company number should be available in the conversation history or context."
        "return the summary of company credit risk details in the response"
    ),
    tools=[get_company_charges, get_company_insolvency],
    output_key="credit_risk_result"
)

compliance_kyc_agent = Agent(
    name="compliance_kyc_agent",
    # model="gemini-2.5-flash",
    model=config.gemini_model,
    description=(
        "You are an agent helping to analyse companies compliance and KYC details from company details from the companies house database"
    ),
    instruction=(
        "You are an agent for getting company compliance and KYC details in the companies house database"
        "Use the get_company_officers, get_company_exemptions, get_corporate_officer_disqualifications, get_natural_officer_disqualifications, get_office_appointments tools to get relevant data"
        "The company number should be available in the conversation history or context."
        "return the summary of company compliance and KYC details in the response"
    ),
    tools=[get_company_officers, get_company_exemptions, get_corporate_officer_disqualifications, get_natural_officer_disqualifications, get_office_appointments],
    output_key="compliance_kyc_result"
)

corporate_structure_agent = Agent(
    name="corporate_structure_agent",
    # model="gemini-2.5-flash",
    model=config.gemini_model,
    description=(
        "You are an agent helping to analyse companies corporate structure from company details from the companies house database"
    ),
    instruction=(
        "You are an agent for getting company corporate structure details in the companies house database"
        "Use the get_company_establishments and get_company_registers tools"
        "The company number should be available in the conversation history or context."
        "return the summary of company corporate structure details in the response"
    ),
    tools=[get_company_establishments, get_company_registers],
    output_key="corporate_structure_result"
)

filing_history_agent = Agent(
    name="filing_history_agent",
    # model="gemini-2.5-flash",
    model=config.gemini_model,
    description=(
        "You are an agent helping to analyse companies filings history from company details from the companies house database"
    ),
    instruction=(
        "You are an agent for getting company filing history details in the companies house database"
        "Use the get_company_filing_history tool to get the list of company filings"
        "Then use the get_company_filing_detail tool to get the details for the 3 most recent filings."
        "The company number should be available in the conversation history or context."
        "return the summary of company filings history details and the specific details of these 3 filings in the response"
    ),
    tools=[get_company_filing_history, get_company_filing_detail],
    output_key="company_filing_history_result"
)

def registerendcallback(callback_context: CallbackContext):
   callback_context.state['final_message'] = True

company_report_creation_agent =  Agent(
    name="company_report_creation_agent",
    # model="gemini-2.5-flash",
    model=config.gemini_model,
    description=(
        "You are an agent helping a final report on a company based on the data retrieved from the companies house database"
    ),
    instruction=(
        "You are a report creation agent for getting company details in the companies house database"
        "Input summaries: use the results from previous agents (search_companies_google_agent, get_company_profile_agent, etc.) which are available in your conversation history or context."
        "Use all the above retrieved details to create a report that can be used to assess the company"
        "Make the report detailed and have a section at the end that is a viability assessment of the company"
        "Use only the data retrieved by all the previous agents to asses the company viability"
        "Make the report comprehensive"
    ),
    after_agent_callback=registerendcallback
)

data_retrieval_agent = ParallelAgent(
    name="data_retrieval_agent",
    description=(
        "You are an agent that helps a retreive info about a company"
    ),
    sub_agents=[
        get_company_profile_agent,
        get_company_officers_agent,
        search_companies_google_agent,
        credit_risk_agent,
        compliance_kyc_agent,
        corporate_structure_agent,
        filing_history_agent
    ]
)

report_generation_agent = SequentialAgent(
    name="report_generation_agent",
    description="Generates a comprehensive report on a company.",
    sub_agents=[
        search_companies_agent,
        data_retrieval_agent,
        company_report_creation_agent
    ]
)


root_agent = Agent(
    name="root_agent",
    model=config.gemini_model,
    description="Companies House Assistant. Uses tools to answer questions, or transfers to report_generation_agent for full reports.",
    instruction=(
        "You are a Companies House Assistant. You have access to tools."
        "**Guideline**: Use tools directly to answer specific questions whenever possible."
        "1. If you need to find a company number from a name, use the `search_companies` tool."
        "2. To get general profile details, use the `get_company_profile` tool."
        "3. To get officer details, use the `get_company_officers` tool."
        "4. To check charges, use the `get_company_charges` tool."
        "5. To check insolvency, use the `get_company_insolvency` tool."
        "6. To get filing history, use the `get_company_filing_history` tool."
        "7. To get corporate structure, use the `get_company_establishments` and `get_company_registers` tools."
        "8. If the user explicitly asks for a **full report** or a comprehensive analysis, transfer to `report_generation_agent`."
        "**Important**: You are a concise question-answering system. Answer specific questions in a single **short** natural language sentence. Do NOT use bullet points, lists, headers, or bold text. Just provide the direct answer to the question."
    ),
    tools=[
        get_company_profile, get_company_officers, get_company_charges, get_company_insolvency, search_companies,
        get_company_establishments, get_company_registers, get_company_filing_history, get_company_filing_detail
    ],
    sub_agents=[
        report_generation_agent
    ]
)