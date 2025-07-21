import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Trash2 } from 'lucide-react';
import './App.css';
import ReactMarkdown from 'react-markdown';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState('');
  const messagesEndRef = useRef(null);
  const [conversationId] = useState('default');
  const eventSourceRef = useRef(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentStreamingMessage]);

  // 发送消息并处理流式响应（fetch + ReadableStream 实现）
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setCurrentStreamingMessage('');

    try {
      // 关闭上一个流（如果有）
      if (eventSourceRef.current) {
        eventSourceRef.current.cancel && eventSourceRef.current.cancel();
        eventSourceRef.current = null;
      }

      // fetch POST 流式请求
      const controller = new AbortController();
      eventSourceRef.current = controller;

      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_id: conversationId
        }),
        signal: controller.signal
      });

      if (!response.ok || !response.body) {
        throw new Error('Network response was not ok');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let fullMessage = '';

      while (!done) {
        const { value, done: streamDone } = await reader.read();
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          setCurrentStreamingMessage(prev => prev + chunk);
          fullMessage += chunk;
        }
        done = streamDone;
      }

      // 流结束，推送到 messages
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: fullMessage,
          timestamp: new Date().toISOString()
        }
      ]);
      setCurrentStreamingMessage('');
      setIsLoading(false);

    } catch (error) {
      setIsLoading(false);
      setCurrentStreamingMessage('');
      const errorMessage = {
        role: 'assistant',
        content: '抱歉，发生了错误，请稍后重试。',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // 清空对话
  const clearConversation = async () => {
    try {
      await axios.delete(`http://localhost:8000/conversations/${conversationId}`);
      setMessages([]);
      setCurrentStreamingMessage('');
    } catch (error) {
      console.error('Error clearing conversation:', error);
    }
  };

  // 回车发送
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 时间格式化
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <h1>LangGraph 聊天助手</h1>
          <button 
            className="clear-button"
            onClick={clearConversation}
            title="清空对话"
          >
            <Trash2 size={20} />
          </button>
        </div>

        <div className="messages-container">
          {messages.map((message, index) => {
            console.log('渲染message:', message);
            return (
              <div 
                key={index} 
                className={`message ${message.role} ${message.isError ? 'error' : ''}`}
              >
                <div className="message-avatar">
                  {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>
                <div className="message-content">
                  <div className="message-text">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                  <div className="message-time">{formatTime(message.timestamp)}</div>
                </div>
              </div>
            );
          })}
          
          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar">
                <Bot size={20} />
              </div>
              <div className="message-content">
                <div className="message-text streaming">
                  <ReactMarkdown>{currentStreamingMessage}</ReactMarkdown>
                  <span className="cursor">|</span>
                </div>
                <div className="message-time">正在输入...</div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的消息..."
              disabled={isLoading}
              rows={1}
            />
            <button 
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="send-button"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 