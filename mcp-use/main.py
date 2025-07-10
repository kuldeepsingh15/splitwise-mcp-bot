import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient

# Load environment variables
load_dotenv()

# Get Google API key from environment
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required")


async def main():
    # Load environment variables
    load_dotenv()

    # Create configuration dictionary
    config = {
        "mcpServers": {
            "splitwise": {
                "command": "npx",
                "args": [
                    "mcp-remote",
                    "http://localhost:4200/mcp/"
                ]
            }
        }
    }

    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)
    print("client")
    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    print("llm")

    # Define system prompt
    system_prompt = """You are a helpful financial assistant that works with Splitwise data. Your responses should follow these guidelines:

1. ALWAYS return human-readable names instead of IDs (user names, group names, expense names, etc.)
2. NEVER return raw IDs, user IDs, group IDs, or any technical identifiers
3. Provide brief analysis and insights with your results, not just bare data
4. Format your responses in a clear, organized manner
5. When showing balances or debts, explain what the numbers mean in simple terms
6. Use friendly, conversational language while being informative

Remember: Always prioritize names over IDs and provide context with your analysis."""

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30, system_prompt=system_prompt)
    print("agent")
    # Run the query
    result = await agent.run(
        "who owes me money? give me detailed information",
    )
    print(f"\nResult: {result}")


if __name__ == "__main__":
    asyncio.run(main())