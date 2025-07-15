import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

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
    chat_history: list = []  # List of previous messages
    browser_id: str | None = None

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
    logging.info("MCP Client initialized")

    # Create LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    logging.info("LLM initialized")

    # Define system prompt
    system_prompt = """You are a helpful financial assistant and general-purpose assistant.

Guidelines:
1. For general queries, answer naturally and helpfully, just like a friendly assistant. Do not mention Splitwise unless the user asks about it or about expenses, groups, or friends.
2. If the user asks about Splitwise, call the appropriate Splitwise tool (such as get_current_user) directly, using the information provided by the application. Do not ask the user for any internal variables or IDs.
3. NEVER mention or ask for internal variables, IDs, or technical details such as 'browser_id' or any implementation details. Do not instruct the user to look for such variables.
4. If a Splitwise tool returns a login link, always send it to the frontend as a clearly marked clickable link, e.g., 'Login Link: https://...'.
5. If there is no browser_id in the query, politely ask the user to reload the page to continue instaed of assuming.
6. ALWAYS return human-readable names instead of IDs (user names, group names, expense names, etc.)
7. NEVER return raw IDs, user IDs, group IDs, or any technical identifiers
8. Provide brief analysis and insights with your results, not just bare data
9. Format your responses in a clear, organized manner
10. When showing balances or debts, explain what the numbers mean in simple terms
11. Use friendly, conversational language while being informative
12. Remember previous conversation context and refer back to it when relevant
13. If the user asks follow-up questions, use the context from previous messages to provide more relevant answers

Remember: Only mention Splitwise if the user asks about it or about expenses, groups, or friends. Never expose internal implementation details. Always prioritize names over IDs and provide context with your analysis. Use the conversation history to provide more personalized and contextual responses."""

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30, system_prompt=system_prompt)
    logging.info("Agent initialized")

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
    """Process a financial query using the MCP agent with chat context"""
    try:
        if agent is None:
            raise HTTPException(status_code=500, detail="Agent not initialized")
        
        # Extract browser_id from request if present
        browser_id = getattr(request, 'browser_id', None)
        logging.info(f"browser_id: {browser_id}")
        # Build context from chat history (limit to last 10 messages to prevent token overflow)
        context = ""
        if request.chat_history:
            # Take only the last 10 messages to manage context length
            recent_history = request.chat_history[-10:]
            
            # If we have more than 10 messages, create a summary of earlier conversation
            if len(request.chat_history) > 10:
                earlier_messages = request.chat_history[:-10]
                user_topics = []
                for msg in earlier_messages:
                    if isinstance(msg, dict) and 'user' in msg:
                        user_topics.append(msg['user'][:100])  # First 100 chars of each user message
                
                context = f"Earlier conversation covered: {', '.join(user_topics[:5])}...\n\n"
            
            context += "Recent conversation:\n"
            for i, msg in enumerate(recent_history):
                if isinstance(msg, dict):
                    if 'user' in msg:
                        context += f"User: {msg['user']}\n"
                    elif 'server' in msg:
                        # Truncate long assistant responses to keep context manageable
                        assistant_msg = msg['server']
                        if len(assistant_msg) > 500:
                            assistant_msg = assistant_msg[:500] + "..."
                        context += f"Assistant: {assistant_msg}\n"
                else:
                    context += f"Message {i+1}: {msg}\n"
            context += "\nCurrent query: "
        
        # Combine context with current query
        full_query = context + request.query if context else request.query
        
        # Run the query with full context
        full_query_with_id = f"[browser_id: {browser_id}]\n{full_query}" if browser_id else full_query
        result = await agent.run(full_query_with_id)
        
        return QueryResponse(
            result=result,
            success=True
        )
    
    except Exception as e:
        logging.exception("Error processing query")
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

@app.post("/debug-context")
async def debug_context(request: QueryRequest):
    """Debug endpoint to see how context is being built"""
    try:
        # Build context from chat history (same logic as main endpoint)
        context = ""
        if request.chat_history:
            recent_history = request.chat_history[-10:]
            
            if len(request.chat_history) > 10:
                earlier_messages = request.chat_history[:-10]
                user_topics = []
                for msg in earlier_messages:
                    if isinstance(msg, dict) and 'user' in msg:
                        user_topics.append(msg['user'][:100])
                
                context = f"Earlier conversation covered: {', '.join(user_topics[:5])}...\n\n"
            
            context += "Recent conversation:\n"
            for i, msg in enumerate(recent_history):
                if isinstance(msg, dict):
                    if 'user' in msg:
                        context += f"User: {msg['user']}\n"
                    elif 'server' in msg:
                        assistant_msg = msg['server']
                        if len(assistant_msg) > 500:
                            assistant_msg = assistant_msg[:500] + "..."
                        context += f"Assistant: {assistant_msg}\n"
                else:
                    context += f"Message {i+1}: {msg}\n"
            context += "\nCurrent query: "
        
        full_query = context + request.query if context else request.query
        
        return {
            "original_query": request.query,
            "chat_history_length": len(request.chat_history) if request.chat_history else 0,
            "context_built": context,
            "full_query": full_query,
            "context_length": len(full_query)
        }
    
    except Exception as e:
        logging.exception("Error in debug-context endpoint")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "80")))