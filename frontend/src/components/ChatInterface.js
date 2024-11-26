import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ChatInterface.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001';

const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [conversation, setConversation] = useState([]);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Test backend connection on component mount
    const testBackendConnection = async () => {
      try {
        await axios.post(`${BACKEND_URL}/api/ask`, 
          { question: 'test' },
          {
            headers: { 
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*'
            },
            withCredentials: false,
            timeout: 60000
          }
        );
        console.log('Backend connection successful');
      } catch (err) {
        console.log('Backend connection test:', err.message);
        setError('Unable to connect to backend server. Please check if it\'s running.');
      }
    };
    testBackendConnection();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    if (!input.trim()) {
      setError('Please enter a question');
      setIsLoading(false);
      return;
    }
    
    const newQuestion = { type: 'question', content: input };
    setConversation(prev => [...prev, newQuestion]);
    
    try {
      console.log('Sending request to:', `${BACKEND_URL}/api/ask`);
      
      const result = await axios.post(
        `${BACKEND_URL}/api/ask`, 
        { question: input },
        {
          headers: { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          },
          withCredentials: false,  // Important for CORS
          timeout: 60000  // Increased timeout to 60 seconds
        }
      );
      
      console.log('Response received:', result.data);
      
      if (result.data && result.data.answer) {
        const newAnswer = { 
          type: 'answer', 
          content: result.data.answer,
          sources: result.data.sources || []
        };
        setConversation(prev => [...prev, newAnswer]);
      } else {
        throw new Error('Invalid response format from server');
      }
    } catch (err) {
      console.error('Error details:', err);
      const errorMessage = err.response?.data?.error || 
                          err.message || 
                          'An error occurred while connecting to the server';
      setError(errorMessage);
      
      const errorResponse = {
        type: 'answer',
        content: `Error: ${errorMessage}`,
        sources: []
      };
      setConversation(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
      setInput('');
    }
  };

  const formatMessage = (content) => {
    if (!content) return null;
    
    try {
      const codeBlockRegex = /```[\s\S]*?```/g;
      const bulletPointRegex = /^\s*[-*]\s(.+)$/gm;
      const numberedListRegex = /^\s*(\d+\.)\s(.+)$/gm;

      const parts = content.split(codeBlockRegex);
      const codeBlocks = content.match(codeBlockRegex) || [];
      
      return parts.reduce((acc, part, index) => {
        // Format bullet points
        part = part.replace(bulletPointRegex, '<li>$1</li>');
        if (part.includes('<li>')) {
          part = `<ul>${part}</ul>`;
        }
        
        // Format numbered lists
        part = part.replace(numberedListRegex, '<li>$2</li>');
        if (part.includes('<li>') && !part.includes('<ul>')) {
          part = `<ol>${part}</ol>`;
        }

        acc.push(<span key={`text-${index}`} dangerouslySetInnerHTML={{ __html: part }} />);
        
        if (codeBlocks[index]) {
          const code = codeBlocks[index].replace(/```/g, '').trim();
          acc.push(
            <pre key={`code-${index}`} className="code-block">
              <code>{code}</code>
            </pre>
          );
        }
        return acc;
      }, []);
    } catch (error) {
      console.error('Error formatting message:', error);
      return <span>{content}</span>;
    }
  };

  return (
    <div className="chat-interface">
      {error && <div className="error-banner">{error}</div>}
      
      <div className="conversation">
        {conversation.map((msg, index) => (
          <div key={index} className={`message ${msg.type} ${msg.type === 'answer' && isLoading ? 'loading' : ''}`}>
            <strong>{msg.type === 'question' ? 'Q: ' : 'A: '}</strong>
            {formatMessage(msg.content)}
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                <strong>Sources:</strong>
                <ul>
                  {msg.sources.map((source, idx) => (
                    <li key={idx}>{source}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="loading-indicator">
            Processing your question...
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;