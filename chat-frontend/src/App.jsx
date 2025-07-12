import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import Login from './components/Login';
import Register from './components/Register';
import './App.css'

export default function App() {
  const [chatHistory, setChatHistory] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [showContextInfo, setShowContextInfo] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [showRegister, setShowRegister] = useState(false);
  const [user, setUser] = useState(null);
  const chatEndRef = useRef(null);

  // Check for existing token on component mount
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      setIsAuthenticated(true);
      // Verify token is still valid
      verifyToken(savedToken);
    }
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, loading]);

  const verifyToken = async (tokenToVerify) => {
    try {
      const response = await fetch('http://localhost:8000/me', {
        headers: {
          'Authorization': `Bearer ${tokenToVerify}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setIsAuthenticated(true);
        setToken(tokenToVerify);
      } else {
        // Token is invalid, clear it
        localStorage.removeItem('token');
        setIsAuthenticated(false);
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      setToken(null);
      setUser(null);
    }
  };

  const handleLogin = (newToken) => {
    setToken(newToken);
    setIsAuthenticated(true);
    setShowRegister(false);
    verifyToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setToken(null);
    setUser(null);
    setChatHistory([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading || !token) return;

    const newHistory = [...chatHistory, { user: input }];
    setChatHistory(newHistory);
    setInput("");
    setLoading(true);

    try {
      // Prepare chat history for context
      const chatContext = chatHistory.map(msg => {
        if (msg.user) return { user: msg.user };
        if (msg.server) return { server: msg.server };
        return msg;
      });

      const res = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ 
          query: input,
          chat_history: chatContext
        }),
      });
      
      if (res.status === 401) {
        // Token expired or invalid
        handleLogout();
        setChatHistory([
          ...newHistory,
          { server: "Your session has expired. Please log in again.", type: "text" },
        ]);
        return;
      }
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      
      if (data.success) {
        setChatHistory([
          ...newHistory,
          { server: data.result, type: "markdown" },
        ]);
      } else {
        setChatHistory([
          ...newHistory,
          { server: `Error: ${data.error || "Unknown error occurred"}`, type: "text" },
        ]);
      }
    } catch (err) {
      setChatHistory([
        ...newHistory,
        { server: `Error: Could not connect to server. Please make sure the backend is running on localhost:8000.`, type: "text" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = (msg, idx) => {
    if (msg.user)
      return (
        <div key={idx} className="msg user">
          <div className="bubble">{msg.user}</div>
        </div>
      );
    if (msg.server) {
      if (msg.type === "table") {
        return (
          <div key={idx} className="msg server">
            <div className="bubble">
              <table>
                <tbody>
                  {msg.server.map((row, i) => (
                    <tr key={i}>
                      {row.map((cell, j) => (
                        <td key={j}>{cell}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      }
      if (msg.type === "list") {
        return (
          <div key={idx} className="msg server">
            <div className="bubble">
              <ul>
                {msg.server.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        );
      }
      return (
        <div key={idx} className="msg server">
          <div className="bubble">
            <ReactMarkdown>{msg.server}</ReactMarkdown>
          </div>
        </div>
      );
    }
    return null;
  };

  // Show authentication screens if not authenticated
  if (!isAuthenticated) {
    return (
      <div style={{
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#18191c',
        fontFamily: 'Segoe UI, Roboto, Arial, sans-serif'
      }}>
        {showRegister ? (
          <Register 
            onRegister={handleLogin}
            onSwitchToLogin={() => setShowRegister(false)}
            onLogin={handleLogin}
          />
        ) : (
          <Login 
            onLogin={handleLogin}
            onSwitchToRegister={() => setShowRegister(true)}
          />
        )}
      </div>
    );
  }

  // Show chat interface if authenticated
  return (
    <div className="chat-outer">
      <header className="chat-header">
        <div className="chat-header-title">Financial Assistant</div>
        <div className="chat-header-desc">Your Splitwise AI Assistant</div>
        <div style={{
          position: 'absolute',
          right: '20px',
          top: '50%',
          transform: 'translateY(-50%)',
          display: 'flex',
          gap: '10px',
          alignItems: 'center'
        }}>
          {user && (
            <span style={{
              fontSize: '12px',
              color: '#bbdefb',
              marginRight: '10px'
            }}>
              Welcome, {user.username}
            </span>
          )}
          <button 
            onClick={() => setShowContextInfo(!showContextInfo)}
            style={{
              background: 'transparent',
              border: '1px solid #38bdf8',
              color: '#38bdf8',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            {showContextInfo ? 'Hide' : 'Show'} Context
          </button>
          <button 
            onClick={handleLogout}
            style={{
              background: 'transparent',
              border: '1px solid #ef4444',
              color: '#ef4444',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Logout
          </button>
        </div>
      </header>
      <div className="chat-card">
        <div className="chat-history" id="chat-history">
          {showContextInfo && chatHistory.length > 0 && (
            <div style={{
              background: 'rgba(56, 189, 248, 0.1)',
              border: '1px solid #38bdf8',
              borderRadius: '8px',
              padding: '12px',
              margin: '10px',
              fontSize: '12px',
              color: '#38bdf8'
            }}>
              <strong>Context Info:</strong> {chatHistory.length} messages in conversation
              {chatHistory.length > 10 && (
                <span style={{marginLeft: '10px', color: '#fbbf24'}}>
                  (Showing last 10 for context)
                </span>
              )}
            </div>
          )}
          {chatHistory.map((msg, idx) => renderMessage(msg, idx))}
          {loading && (
            <div className="msg server">
              <div className="bubble thinking">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
                &nbsp;Thinking...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
      </div>
      <form className="chat-input-row" onSubmit={handleSubmit} autoComplete="off">
        <textarea
          rows={1}
          className="chat-textarea"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          placeholder="Type your message..."
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button type="submit" className="chat-send-btn" disabled={loading || !input.trim()}>
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style={{cursor:'pointer',display:'block'}}>
            <defs>
              <linearGradient id="sendArrowGradient" x1="8" y1="8" x2="28" y2="24" gradientUnits="userSpaceOnUse">
                <stop stopColor="#38bdf8"/>
                <stop offset="1" stopColor="#34d399"/>
              </linearGradient>
            </defs>
            <path d="M8 16H28M19 8l9 8-9 8" stroke="url(#sendArrowGradient)" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </form>
      <style>{`
        html, body, #root {
          height: 100%;
          min-height: 100%;
          margin: 0;
          padding: 0;
          box-sizing: border-box;
          font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
          background: #18191c;
          color: #f3f4f6;
          overflow: hidden;
        }
        .chat-outer {
          display: flex;
          flex-direction: column;
          height: 100vh;
          width: 100vw;
          align-items: center;
        }
        .chat-header {
          flex-shrink: 0;
          padding: 0;
          background: transparent;
          text-align: center;
          margin: 0;
          border-radius: 0;
          width: 100%;
          max-width: 900px;
        }
        .chat-header-title {
          font-size: 2.3rem;
          font-weight: 700;
          color: #fff;
          letter-spacing: 0.5px;
        }
        .chat-header-desc {
          font-size: 1rem;
          color: #bbdefb;
          margin-top: 2px;
        }
        .chat-card {
          flex: 1 1 0;
          min-height: 0;
          width: 100%;
          max-width: 900px;
          display: flex;
          flex-direction: column;
        }
        .chat-history {
          flex: 1 1 0;
          min-height: 0;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 18px;
          width: 100%;
          padding-right: 32px;
          scrollbar-width: thin;
          scrollbar-color: #444 #222;
        }
        .chat-history::-webkit-scrollbar {
          width: 8px;
          background: #222;
        }
        .chat-history::-webkit-scrollbar-thumb {
          background: #444;
          border-radius: 8px;
        }
        .chat-history::-webkit-scrollbar-button {
          display: none;
        }
        .msg {
          display: flex;
        }
        .msg.user {
          justify-content: flex-end;
        }
        .msg.server {
          justify-content: flex-start;
        }
        .bubble {
          padding: 14px 20px;
          border-radius: 18px;
          max-width: 60%;
          font-size: 1.08rem;
          line-height: 1.7;
          box-shadow: 0 1.5px 6px #00000033;
          transition: background 0.2s;
          word-break: break-word;
        }
        .msg.user .bubble {
          background: #232428;
          color: #fff;
          border-bottom-right-radius: 18px;
          text-align: right;
        }
        .msg.server .bubble {
          background: #26272b;
          color: #e3e4e8;
          border-bottom-left-radius: 18px;
          text-align: left;
        }
        .chat-input-row {
          flex-shrink: 0;
          width: 100%;
          max-width: 900px;
          display: flex;
          align-items: flex-end;
          background: transparent;
          margin: 0;
          padding: 0;
          position: relative;
          justify-content: center;
          margin-bottom: 36px;
        }
        .chat-textarea {
          flex: 1;
          min-height: 48px;
          max-height: 120px;
          resize: none;
          border-radius: 18px;
          border: none;
          padding: 18px 60px 18px 18px;
          font-size: 1.1rem;
          outline: none;
          box-shadow: 0 2px 16px #00000022;
          background: #232428;
          color: #fff;
          margin: 0;
          width: 100%;
        }
        .chat-textarea:focus {
          background: #232428;
        }
        .chat-send-btn {
          background: transparent;
          border: none;
          box-shadow: none;
          color: #fff;
          cursor: pointer;
          padding: 8px;
          border-radius: 50%;
          transition: all 0.2s ease;
          position: absolute;
          right: 18px;
          top: 50%;
          transform: translateY(-50%);
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
        }
        .chat-send-btn:disabled {
          background: transparent;
          color: #b0b0b5;
          cursor: not-allowed;
        }
        .thinking {
          display: flex;
          align-items: center;
        }
        .dot {
          height: 8px;
          width: 8px;
          margin: 0 2px;
          background: #fff;
          border-radius: 50%;
          display: inline-block;
          animation: blink 1.4s infinite both;
        }
        .dot:nth-child(1) { animation-delay: 0s; }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes blink { 0%, 80%, 100% { opacity: 0.2; } 40% { opacity: 1; } }
        table { border-collapse: collapse; margin: 8px 0; background: #232428; border-radius: 8px; overflow: hidden; }
        td, th { border: 1px solid #35363c; padding: 6px 12px; color: #fff; }
        @media (max-width: 700px) {
          .chat-header, .chat-main, .chat-input { max-width: 100vw; }
          .chat-main { padding: 0 2vw; }
        }
      `}</style>
    </div>
  );
}
