import os
from alias import *
from agent import Agent


async def myFunc():
    API_KEY = os.getenv('CODEGPT_API_KEY')
    AGENT_ID = os.getenv('CODEGPT_AGENT_ID')

    agent = Agent(API_KEY, AGENT_ID)

    prompt = "can you help me?"

    response = await agent.chat_completion(prompt,stream=True)
    
    print(response)

if __name__ == "__main__":
    codegpt(myFunc())