// frontend/src/App.tsx
import { useState, useEffect, useRef } from 'react';
import Feedback from './components/Feedback';
import './index.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      text: "Hello! I am your JIT Retrieval Agent. Ask me anything about the docs you have access to.",
      sender: 'agent',
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      });

      if (!response.ok) throw new Error('Failed to reach agent');

      const data = await response.json();
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response || "Sorry, I encountered an issue.",
        sender: 'agent',
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: 'error',
          text: "System Error: Unable to communicate with the ADK agent.",
          sender: 'agent',
          timestamp: new Date().toLocaleTimeString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (messageId: string, rating: 'up' | 'down') => {
    console.log(`Feedback for ${messageId}: ${rating}`);
    try {
      await fetch('/api/v1/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messageId, rating }),
      });
    } catch (err) {
      console.error('Failed to log feedback', err);
    }
  };

  return (
    <div className="chat-app">
      <header className="chat-header">
        <h1>JIT Two-Stage RAG</h1>
        <div className="status-indicator">
          <span className="dot"></span> Active
        </div>
      </header>

      <main className="chat-window">
        {messages.map((m) => (
          <div key={m.id} className={`message-wrapper ${m.sender}`}>
            <div className={`message-bubble ${m.sender}`}>
              <div className="message-content">{m.text}</div>
              <div className="message-footer">
                <span className="timestamp">{m.timestamp}</span>
                {m.sender === 'agent' && (
                  <Feedback messageId={m.id} onFeedback={handleFeedback} />
                )}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message-wrapper agent">
            <div className="message-bubble agent loading">
              <span className="dot-typing"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      <footer className="chat-input-area">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            sendMessage();
          }}
        >
          <input
            type="text"
            placeholder="Type your question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </button>
        </form>
      </footer>
    </div>
  );
}

export default App;
