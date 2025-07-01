# import os
# import asyncio
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from agents.data_agent import data_analysis_agent

# async def main():
#     # Initialize runner with session service
#     runner = Runner(
#         agent=data_analysis_agent,
#         session_service=InMemorySessionService()
#     )
    
#     # Example interaction
#     response = await runner.run_async(
#         "Please analyze data.csv and tell me the average balance by gender and job classification"
#     )
#     print("Response:", response)

# if __name__ == "__main__":
#     # Load environment variables
#     from dotenv import load_dotenv
#     load_dotenv()
    
#     # Run the async main function
#     asyncio.run(main())

import os
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from ..root_agent import root_agent  # Updated import

async def main():
    # Initialize runner with session service
    runner = Runner(
        agent=root_agent,  # Use the root_agent directly
        session_service=InMemorySessionService()
    )
    
    # First load the data
    await runner.run_async("Please load data.csv")
    
    # Then perform analysis
    response = await runner.run_async(
        "What is the average balance by gender and job classification?"
    )
    print("Response:", response)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(main())