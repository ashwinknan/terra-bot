import React, { useState } from 'react';
import axios from 'axios';
import './ChatInterface.css';

//const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001';
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://rag-game-assistant-backend.onrender.com';

const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [conversation, setConversation] = useState([]);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const newQuestion = { type: 'question', content: input };
    setConversation(prev => [...prev, newQuestion]);
    
    try {
      const result = await axios.post(`${BACKEND_URL}/ask`, { question: input }, {
        headers: { 'Content-Type': 'application/json' },
      });
      
      const newAnswer = { 
        type: 'answer', 
        content: result.data.answer,
        sources: result.data.sources
      };
      setConversation(prev => [...prev, newAnswer]);
    } catch (err) {
      console.error('Error:', err);
      setError(err.response?.data?.error || 'An error occurred');
    }
    
    setInput('');
  };

  const formatMessage = (content) => {
    const codeBlockRegex = /```[\s\S]*?```/g;
    const bulletPointRegex = /^\s*[-*]\s(.+)$/gm;
    const numberedListRegex = /^\s*(\d+\.)\s(.+)$/gm;

    const parts = content.split(codeBlockRegex);
    const codeBlocks = content.match(codeBlockRegex) || [];
    
    return parts.reduce((acc, part, index) => {
      // Format bullet points
      part = part.replace(bulletPointRegex, '<li>$1</li>');
      part = part.replace(/<li>/g, '<ul><li>').replace(/<\/li>\s*(?!<li>)/g, '</li></ul>');
      
      // Format numbered lists
      part = part.replace(numberedListRegex, '<li>$2</li>');
      part = part.replace(/<li>/g, '<ol><li>').replace(/<\/li>\s*(?!<li>)/g, '</li></ol>');

      acc.push(<span key={`text-${index}`} dangerouslySetInnerHTML={{ __html: part }} />);
      
      if (codeBlocks[index]) {
        const code = codeBlocks[index].replace(/```/g, '').trim();
        acc.push(<pre key={`code-${index}`}><code>{code}</code></pre>);
      }
      return acc;
    }, []);
  };

  return (
    <div className="chat-interface">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question"
        />
        <button type="submit">Send</button>
      </form>
      <div className="conversation">
        {conversation.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            <strong>{msg.type === 'question' ? 'Q: ' : 'A: '}</strong>
            {formatMessage(msg.content)}
            {msg.sources && (
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
      </div>
      {error && <div className="error">{error}</div>}
    </div>
  );
};

export default ChatInterface;