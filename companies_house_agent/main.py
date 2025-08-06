from companies_house_agent.agent import root_agent
import asyncio

def main():
    """Runs the Companies House agent."""
    print("Companies House Agent")
    print("--------------------")
    print("Enter your query below. Type 'exit' to quit.")

    while True:
        try:
            query = input("> ")
            if query.lower() == "exit":
                break
            response = asyncio.run(root_agent.query(query))
            print(response)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
