import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
from sqlalchemy.orm import Session
from datetime import timedelta
import json
from datetime import datetime

# Import our custom modules
from database import get_db, User
from auth import get_password_hash, verify_password, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES

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

# Security
security = HTTPBearer()

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    chat_history: list = []  # List of previous messages

class QueryResponse(BaseModel):
    result: str
    success: bool
    error: str | None = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str

# Global variables for client and agent
client = None
agent = None

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    
    if not token or token == "null" or token == "undefined":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def initialize_mcp():
    """Initialize MCP client and agent"""
    global client, agent
    
    try:
        # Create configuration dictionary
        config = {
            "mcpServers": {
                "splitwise": {
                    "url": "http://localhost:4200/mcp/"
                }
            }
        }

        # Create MCPClient from configuration dictionary
        client = MCPClient.from_dict(config)
        print("✅ MCP Client initialized")

        # Create LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        print("✅ LLM initialized")

        # Define system prompt
        system_prompt = """You are a helpful financial assistant that works with Splitwise data. Your responses should follow these guidelines:

1. ALWAYS return human-readable names instead of IDs (user names, group names, expense names, etc.)
2. NEVER return raw IDs, user IDs, group IDs, or any technical identifiers
3. Provide brief analysis and insights with your results, not just bare data
4. Format your responses in a clear, organized manner
5. When showing balances or debts, explain what the numbers mean in simple terms
6. Use friendly, conversational language while being informative
7. Remember previous conversation context and refer back to it when relevant
8. If the user asks follow-up questions, use the context from previous messages to provide more relevant answers

Remember: Always prioritize names over IDs and provide context with your analysis. Use the conversation history to provide more personalized and contextual responses."""

        # Create agent with the client
        agent = MCPAgent(llm=llm, client=client, max_steps=30, system_prompt=system_prompt)
        print("✅ Agent initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize MCP: {str(e)}")
        print("💡 Make sure the MCP server is running on port 4200")


@app.on_event("startup")
async def startup_event():
    """Initialize MCP client and agent on startup"""
    await initialize_mcp()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "MCP Financial Assistant API is running"}

# Authentication endpoints
@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            created_at=db_user.created_at.isoformat()
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")

@app.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = db.query(User).filter(User.username == user_credentials.username).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at.isoformat()
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, current_user: User = Depends(get_current_user)):
    """Process a query using the MCP agent"""
    global client, agent
    
    if not client or not agent:
        return QueryResponse(
            success=False,
            result="",
            error="MCP client not initialized. Please make sure the MCP server is running."
        )
    
    try:
        # Prepare the query with user context
        user_context = f"User: {current_user.username} (ID: {current_user.id})"
        full_query = f"{user_context}\n\nQuery: {request.query}"
        
        # Add chat history for context
        if request.chat_history:
            history_context = "\n\nPrevious conversation:\n"
            for msg in request.chat_history[-5:]:  # Last 5 messages for context
                if 'user' in msg:
                    history_context += f"User: {msg['user']}\n"
                elif 'server' in msg:
                    history_context += f"Assistant: {msg['server']}\n"
            full_query = history_context + "\n" + full_query
        
        print(f"🔍 Processing query for user {current_user.username}: {request.query}")
        
        # Process the query using the run method (async)
        result = await agent.run(full_query)
        
        if result:
            response_content = result
            print(f"✅ Query processed successfully for user {current_user.username}")
            return QueryResponse(
                success=True,
                result=response_content
            )
        else:
            print(f"❌ No valid response from agent for user {current_user.username}")
            return QueryResponse(
                success=False,
                result="",
                error="No response from the AI agent"
            )
            
    except Exception as e:
        print(f"❌ Error processing query for user {current_user.username}: {str(e)}")
        return QueryResponse(
            success=False,
            result="",
            error=f"Error processing query: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global client, agent
    
    mcp_status = "connected" if client and agent else "disconnected"
    
    return {
        "status": "healthy",
        "mcp_status": mcp_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/debug-context")
async def debug_context(request: QueryRequest, current_user: User = Depends(get_current_user)):
    """Debug endpoint to check context and MCP status"""
    global client, agent
    
    debug_info = {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email
        },
        "mcp_status": {
            "client_initialized": client is not None,
            "agent_initialized": agent is not None
        },
        "query": request.query,
        "chat_history_length": len(request.chat_history) if request.chat_history else 0
    }
    
    return debug_info

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 