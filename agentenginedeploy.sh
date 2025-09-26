#!/bin/bash

TARGET_URL="https://discoveryengine.googleapis.com/v1alpha/projects/genaillentsearch/locations/global/collections/default_collection/engines/as-fsi-uki-demo_1758301642647/assistants/default_assistant/agents" # 

JSON_DATA=$(cat <<EOF
{
    "displayName": "Companies House Agent",
    "description": "Allows analysis of UK company data using Companies House API",
    "adk_agent_definition": 
    {
        "tool_settings": {
            "tool_description": "Use the companies house api to search for companies"
        },
        "provisioned_reasoning_engine": {
            "reasoning_engine":"projects/884152252139/locations/us-central1/reasoningEngines/2736662451301908480"
        }
    }
}
EOF
)

echo "Sending POST request to: $TARGET_URL"
echo "Request Body:"
echo "$JSON_DATA"
echo ""

# Perform the POST request using curl
curl -X POST \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -H "X-Goog-User-Project: genaillentsearch" \
     -d "$JSON_DATA" \
     "$TARGET_URL"

echo "" # Add a newline after curl output for better readability
echo "cURL command finished."
