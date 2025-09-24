import asyncio
import uuid
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from companies_house_agent.agent import root_agent


async def main():
    """Runs the Companies House agent."""
    print("Companies House Agent")
    print("--------------------")
    print("Enter your query below. Type 'exit' to quit.")

    session_service = InMemorySessionService()
    APP_NAME = "companies_house_agent"
    USER_ID = "user_1"
    SESSION_ID = "session_001"


    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    runner = Runner(
        agent=root_agent, # The agent we want to run
        app_name=APP_NAME,   # Associates runs with our app
        session_service=session_service # Uses our session manager
    )

    while True:
        try:
            query = await asyncio.to_thread(input, "> ")
            if query.lower() == "exit":
                break

            user_message = types.Content(
                role="user", parts=[types.Part.from_text(text=query)]
            )

            # async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_message):
            #     if event.is_final_response() and event.content:
            #         response = "".join(part.text for part in event.content.parts)
            #         print(f"Agent: {response}")
            async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_message):
                if event.actions and event.actions.state_delta and event.actions.state_delta.get('final_message'):
                    print(f"<<< Agent Response: {event.content}")
                    # You can uncomment the line below to see *all* events during execution
                    # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

                    # Key Concept: is_final_response() marks the concluding message for the turn.
                    if event.is_final_response():
                        if event.content and event.content.parts:
                            # Assuming text response in the first part
                            final_response_text = event.content.parts[0].text
                        elif event.actions and event.actions.escalate: # Handle potential errors/escalations
                            final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                        # Add more checks here if needed (e.g., specific error codes)
                        break # Stop processing events once the final response is found
            # print(f"<<< Agent Response: {final_response_text}")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    asyncio.run(main())