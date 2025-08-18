import asyncio
import uuid

from google.adk.runners import InMemoryRunner
from google.genai import types

from companies_house_agent.agent import root_agent


async def main():
    """Runs the Companies House agent."""
    print("Companies House Agent")
    print("--------------------")
    print("Enter your query below. Type 'exit' to quit.")

    runner = InMemoryRunner(agent=root_agent, app_name="companies_house_agent")
    user_id = str(uuid.uuid4())
    session = await runner.session_service.create_session(
        app_name="companies_house_agent", user_id=user_id
    )

    while True:
        try:
            query = await asyncio.to_thread(input, "> ")
            if query.lower() == "exit":
                break

            user_message = types.Content(
                role="user", parts=[types.Part.from_text(text=query)]
            )

            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=user_message,
            ):
                if event.is_final_response() and event.content:
                    response = "".join(part.text for part in event.content.parts)
                    print(f"Agent: {response}")
                    break
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    asyncio.run(main())