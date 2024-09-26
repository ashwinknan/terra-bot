import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './ChatInterface.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  
  // Simplified scrollToBottom function
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${BACKEND_URL}/ask`, { question: input });
      setConversation([...conversation, { type: 'question', content: input }, { type: 'answer', content: response.data.answer }]);
      setInput('');
    } catch (error) {
      console.error('Error asking question:', error);
      setError('An error occurred while fetching the answer. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatMessage = (content) => {
    const codeRegex = /```csharp([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = codeRegex.exec(content)) !== null) {
      if (match.index > lastIndex) {
        parts.push(content.slice(lastIndex, match.index));
      }
      parts.push(
        <SyntaxHighlighter language="csharp" style={vscDarkPlus} key={match.index}>
          {match[1].trim()}
        </SyntaxHighlighter>
      );
      lastIndex = match.index + match[0].length;
    }

    if (lastIndex < content.length) {
      parts.push(content.slice(lastIndex));
    }

    return parts;
  };

  return (
    <div className="chat-interface">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
      <div className="conversation">
        {conversation.map((entry, index) => (
          <div key={index} className={`message ${entry.type}`}>
            <strong>{entry.type === 'question' ? 'You: ' : 'Assistant: '}</strong>
            {formatMessage(entry.content)}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  );
};

export default ChatInterface;