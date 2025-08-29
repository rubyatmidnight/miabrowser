import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent, ChatOpenAI
from screenenv import Sandbox

load_dotenv()

async def main():
    # Start sandbox
    sandbox = Sandbox()
    await sandbox.start()

    # Load config from env
    useAzure = os.getenv('USE_AZURE_OPENAI', 'false').lower() == 'true'
    taskDesc = os.getenv('AGENT_TASK', 'Browse to github.com and find the number of stars for browser-use repo')

    # Setup LLM
    if useAzure:
        llm = ChatOpenAI(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4'),
            api_base=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_type='azure',
            api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2023-05-15'),
            deployment_id=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')
        )
    else:
        llm = ChatOpenAI(model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'))

    # Create browser-use agent
    agent = Agent(
        task=taskDesc,
        llm=llm,
    )
    try:
        await agent.run()
    except Exception as e:
        print(f'Agent error: {e}')  # error log

    # Close sandbox
    await sandbox.close()

asyncio.run(main())