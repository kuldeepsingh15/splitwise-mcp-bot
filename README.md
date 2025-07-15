# Splitwise Gen-AI Project → # Financial Assistant Gen-AI Project

A comprehensive project that integrates Splitwise API with AI capabilities using MCP (Model Context Protocol) and a React frontend. → A next-generation financial assistant platform that leverages AI to help users manage, analyze, and optimize their finances. The current version integrates Splitwise for expense management, but this is just the beginning—future updates will include features like credit report analysis, financial insights, and more.

## Project Overview

This project aims to become your all-in-one financial assistant. While the initial release focuses on Splitwise integration for group expense management, our roadmap includes:
- Fetching and analyzing credit reports
- Personalized financial insights and recommendations
- Budget tracking and optimization
- Integration with additional financial data sources
- And much more!

Splitwise is just one part of the broader vision to provide a holistic financial management experience powered by AI.

## Project Structure

```
splitwise gen-ai/
├── chat-frontend/          # React frontend application
├── splitwise-mcp/         # Splitwise MCP server
├── backend/               # MCP client and API server
├── start-all.bat         # Windows batch script to start all services
├── start-all.ps1         # PowerShell script to start all services
└── README.md             # This file
```

## Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Git

## Environment Setup

### 1. Splitwise MCP Server

Navigate to the `splitwise-mcp` directory and set up environment variables:

```bash
cd splitwise-mcp
```

Copy the example environment file:
```bash
cp env.example .env
```

Edit `.env` and add your Splitwise API token:
```env
SPLITWISE_API_TOKEN=your_actual_splitwise_api_token_here
SPLITWISE_BASE_URL=https://secure.splitwise.com/api/v3.0
```

### 2. Backend Server

Navigate to the `backend` directory and set up environment variables:

```bash
cd backend
```

Copy the example environment file:
```bash
cp env.example .env
```

Edit `.env` and add your Google AI API key:
```env
GOOGLE_API_KEY=your_actual_google_api_key_here
MCP_SERVER_URL=http://localhost:4200/mcp/
```

## Installation

### 1. Install Frontend Dependencies

```bash
cd chat-frontend
npm install
```

### 2. Install Python Dependencies

For Splitwise MCP server:
```bash
cd splitwise-mcp
pip install -r requirements.txt
```

For Backend server:
```bash
cd backend
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using Scripts

**Windows (PowerShell):**
```powershell
.\start-all.ps1
```

**Windows (Batch):**
```cmd
start-all.bat
```

### Option 2: Manual Start

1. **Start Splitwise MCP Server:**
   ```bash
   cd splitwise-mcp
   python main.py
   ```

2. **Start Backend Server:**
   ```bash
   cd backend
   python server.py
   ```

3. **Start Frontend:**
   ```bash
   cd chat-frontend
   npm run dev
   ```

## Git Configuration

This project is initialized with Git and includes a comprehensive `.gitignore` file that:

- Ignores all environment files (`.env`)
- Excludes virtual environments (`venv/`, `env/`)
- Ignores Node.js dependencies (`node_modules/`)
- Excludes build artifacts and cache files
- Protects API keys and secrets

### Important Security Notes

1. **Never commit `.env` files** - They contain sensitive API keys
2. **Use `env.example` files** - These are safe to commit and serve as templates
3. **Environment variables are loaded automatically** - The code will look for `.env` files in each project directory

## API Keys Required

1. **Splitwise API Token**: Get from [Splitwise API Documentation](https://secure.splitwise.com/oauth_clients)
2. **Google AI API Key**: Get from [Google AI Studio](https://aistudio.google.com/)

## Development

### Adding New Environment Variables

1. Add the variable to the appropriate `env.example` file
2. Update the code to use `os.getenv()` to read the variable
3. Document the new variable in this README

### Chat Context Management

The application now supports full conversation context:

- **Context Preservation**: The backend maintains conversation history and includes it in each query
- **Smart Truncation**: Long conversations are intelligently summarized to prevent token overflow
- **Context Limits**: Only the last 10 messages are included in full detail
- **Earlier Summary**: For longer conversations, earlier messages are summarized
- **Debug Endpoint**: Use `/debug-context` to see how context is being built

### Testing Context Functionality

Run the test script to verify context handling:
```bash
node test-context.js
```

### Project Structure

- **Frontend**: React app with Vite for fast development
- **Splitwise MCP**: FastMCP server that wraps Splitwise API
- **Backend**: FastAPI server that coordinates between frontend and MCP servers

## Troubleshooting

### Common Issues

1. **"SPLITWISE_API_TOKEN environment variable is required"**
   - Make sure you've created a `.env` file in `splitwise-mcp/`
   - Verify your API token is correct

2. **"GOOGLE_API_KEY environment variable is required"**
   - Make sure you've created a `.env` file in `backend/`
   - Verify your Google AI API key is correct

3. **Port conflicts**
   - Frontend runs on port 5173 (Vite default)
   - MCP Use server runs on port 8000
   - Splitwise MCP server runs on port 4200

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all environment variables are properly configured
5. Submit a pull request

## License

This project is for educational and personal use. Please respect the terms of service for all APIs used. 

---

**Future Roadmap**

We are actively working to expand this platform beyond Splitwise. Planned features include:
- Fetching and analyzing credit reports
- Automated financial health checks
- Smart budgeting tools
- Integration with banks and other financial services
- Advanced analytics and reporting

Stay tuned for updates as we transform this project into a full-featured financial assistant! 