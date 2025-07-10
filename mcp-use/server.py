import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Load environment variables
load_dotenv()

# Get Google API key from environment
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is required")

# Create FastAPI app
app = FastAPI(title="MCP Financial Assistant API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request
class QueryRequest(BaseModel):
    query: str

# Pydantic model for response
class QueryResponse(BaseModel):
    result: str
    success: bool
    error: str | None = None

# Global variables for client and agent
client = None
agent = None

async def initialize_mcp():
    """Initialize MCP client and agent"""
    global client, agent
    
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
    print("MCP Client initialized")

    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    print("LLM initialized")

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
    print("Agent initialized")

@app.on_event("startup")
async def startup_event():
    """Initialize MCP client and agent on startup"""
    await initialize_mcp()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "MCP Financial Assistant API is running"}

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a financial query using the MCP agent"""
    try:
        if agent is None:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        # Run the query
        result = await agent.run(request.query)
        
        return QueryResponse(
            result=result,
            success=True
        )
    
    except Exception as e:
        return QueryResponse(
            result="",
            success=False,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "client_initialized": client is not None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 