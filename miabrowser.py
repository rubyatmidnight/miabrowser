import asyncio
import os
from dotenv import load_dotenv
from browser_use import Agent, ChatOpenAI
from screenenv import Sandbox
import time

load_dotenv()

# Load Mia system prompt from file
def loadMiaPrompt(promptFile='mia_prompt.txt'):
    with open(promptFile, 'r') as f:
        return f.read().strip()

# Helper: ask user via file (no Mia wrapping)
async def askUser(question, msgFile='agent_message.txt', replyFile='user_reply.txt', pollInterval=2):
    with open(msgFile, 'w') as f:
        f.write(question)
    print(question)
    print(f"Waiting for reply in {replyFile}...")
    while True:
        if os.path.exists(replyFile):
            with open(replyFile) as f:
                reply = f.read().strip()
            if reply:
                print(f"User replied: {reply}")
                os.remove(replyFile)
                return reply
        await asyncio.sleep(pollInterval)

async def main():
    # Initialize sandbox (local/VM, no start/close needed)
    print("Initializing sandbox!")
    sandbox = Sandbox()

    # Load config from env
    useAzure = os.getenv('USE_AZURE_OPENAI', 'false').lower() == 'true'
    taskDesc = os.getenv('AGENT_TASK', 'Browse to github.com and find the number of stars for browser-use repo')
    miaSystemPrompt = loadMiaPrompt()

    # Setup LLM
    if useAzure:
        llm = ChatOpenAI(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY')
        )
    else:
        llm = ChatOpenAI(
            model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'),
            api_key=os.getenv('OPENAI_API_KEY')
        )

    # Combine Mia prompt and task
    miaSystemPrompt = loadMiaPrompt()
    taskDesc = os.getenv('AGENT_TASK', 'Browse to github.com and find the number of stars for browser-use repo')
    fullTask = f"{miaSystemPrompt}\n\n{taskDesc}"

    # Example: ask user before running agent
    reply = await askUser("Ready to start agent task? (yes/no)")
    if reply.lower() != 'yes':
        print("Agent stopped by user.")
        return

    # Create browser-use agent
    print("Agent is starting its task!")
    agent = Agent(
        task=fullTask,
        llm=llm,
    )
    try:
        await agent.run()
    except Exception as e:
        print(f'Agent error: {e}')

    print("Sandbox session ended! Bye bye!")

asyncio.run(main())