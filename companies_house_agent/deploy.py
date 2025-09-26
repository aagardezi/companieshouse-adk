import vertexai
from agent import root_agent # modify this if your agent is not in agent.py
import os
from vertexai import agent_engines


# TODO: Fill in these values for your project
PROJECT_ID = os.environ['GOOGLE_CLOUD_PROJECT']
LOCATION = os.environ['GOOGLE_CLOUD_LOCATION']  # For other options, see https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview#supported-regions
STAGING_BUCKET = "gs://agentspace-agents-sg-genaidemos"

# Initialize the Vertex AI SDK
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# Wrap the agent in an AdkApp object
app = agent_engines.AdkApp(
    agent=root_agent,
    enable_tracing=True,
)