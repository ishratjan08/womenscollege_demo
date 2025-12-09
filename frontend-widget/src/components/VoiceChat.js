import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './VoiceChat.css';
import { marked } from 'marked';

const VoiceChat = ({ sessionId: propSessionId, userId: propUserId, backendUrl = 'http://localhost:8000' }) => {
  const [sessionId, setSessionId] = useState(propSessionId);
  const [userId, setUserId] = useState(propUserId);
  const [messages, setMessages] = useState([]);
  const [userQuery, setUserQuery] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [playingAudioId, setPlayingAudioId] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const chatWindowRef = useRef(null);
  const audioRefsRef = useRef({});
  const recordedAudioBlobRef = useRef(null);

  // Initialize session and user IDs from localStorage
  useEffect(() => {
    let storedSessionId = localStorage.getItem('sessionId');
    let storedUserId = localStorage.getItem('userId');

    if (!storedSessionId) {
      storedSessionId = 'session_' + Date.now();
      localStorage.setItem('sessionId', storedSessionId);
    }
    if (!storedUserId) {
      storedUserId = 'user_' + Date.now();
      localStorage.setItem('userId', storedUserId);
    }

    setSessionId(storedSessionId);
    setUserId(storedUserId);

    // Initialize with welcome message
    setMessages([{ sender: 'bot', text: 'Welcome! How can I help you today?', id: 'welcome', audioUrl: null }]);
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [messages]);

  const appendMessage = (sender, message, audioUrl = null) => {
    const messageId = `msg_${Date.now()}_${Math.random()}`;
    setMessages((prev) => [...prev, { sender, text: message, id: messageId, audioUrl }]);
    return messageId;
  };

  const sendMessage = async () => {
    const query = userQuery.trim();
    if (!query) return;

    appendMessage('user', query);
    setUserQuery('');
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(
        `${backendUrl}/api/chat?user_query=${encodeURIComponent(query)}&session_id=${encodeURIComponent(sessionId)}&user_id=${encodeURIComponent(userId)}`,
        {}
      );
      
      // Add bot response without auto-playing
      const botMessage = response.data.Message;
      appendMessage('bot', botMessage);
    } catch (err) {
      console.error('Error:', err);
      appendMessage('bot', 'Sorry, something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    try {
      setError('');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      appendMessage('user', '🎤 Recording audio...');
    } catch (err) {
      setError('Microphone access denied.');
    }
  };

  const stopRecording = async () => {
    if (!mediaRecorderRef.current) return;

    mediaRecorderRef.current.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
      recordedAudioBlobRef.current = audioBlob;
      
      // Remove "Recording audio..." message
      setMessages((prev) => prev.slice(0, -1));
      
      await sendAudio(audioBlob);
      setIsRecording(false);
    };

    mediaRecorderRef.current.stop();
    mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop());
  };

  const sendAudio = async (audioBlob) => {
    setIsLoading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.wav');
      formData.append('session_id', sessionId);
      formData.append('user_id', userId);

      const res = await axios.post(`${backendUrl}/api/chat/audio`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      // Create audio URL from recorded blob and add as audio message
      const audioUrl = URL.createObjectURL(audioBlob);
      appendMessage('user', res.data.text, audioUrl);
      
      // Add bot response with audio URL if available
      const botMessage = res.data.message;
      const botAudioUrl = res.data.audio_url ? `${backendUrl}${res.data.audio_url}` : null;
      appendMessage('bot', botMessage, botAudioUrl);
    } catch (err) {
      console.error('Error:', err);
      setError('Error processing audio.');
      appendMessage('bot', 'Sorry, I could not process your audio.');
    } finally {
      setIsLoading(false);
    }
  };

  // Text-to-Speech synthesis
  const synthesizeAndPlayAudio = async (text) => {
    try {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.volume = 1;
      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.error('Text-to-speech error:', err);
    }
  };

  // Play audio message
  const playAudio = (audioUrl, messageId) => {
    if (playingAudioId === messageId) {
      // Stop playing
      if (audioRefsRef.current[messageId]) {
        audioRefsRef.current[messageId].pause();
        audioRefsRef.current[messageId].currentTime = 0;
      }
      setPlayingAudioId(null);
    } else {
      // Play audio
      if (!audioRefsRef.current[messageId]) {
        audioRefsRef.current[messageId] = new Audio(audioUrl);
      }
      
      const audio = audioRefsRef.current[messageId];
      audio.onended = () => setPlayingAudioId(null);
      audio.play().catch(err => console.error('Audio playback error:', err));
      setPlayingAudioId(messageId);
    }
  };

  const resetSession = () => {
    const newSessionId = 'session_' + Date.now();
    localStorage.setItem('sessionId', newSessionId);
    setSessionId(newSessionId);
    setMessages([{ sender: 'bot', text: 'Session reset. Start a new conversation!', id: 'reset' }]);
  };

  const resetUser = () => {
    const newUserId = 'user_' + Date.now();
    const newSessionId = 'session_' + Date.now();
    localStorage.setItem('userId', newUserId);
    localStorage.setItem('sessionId', newSessionId);
    setUserId(newUserId);
    setSessionId(newSessionId);
    setMessages([{ sender: 'bot', text: 'User and session reset. Welcome back!', id: 'reset-user' }]);
  };

  if (!isOpen) {
    return (
      <button
        className="chatbot-toggle-button"
        onClick={() => setIsOpen(true)}
        title="Open chatbot"
      >
        💬
      </button>
    );
  }

  return (
    <div className={`chatbot-widget ${isMaximized ? 'maximized' : 'open'}`}>
      {/* Header */}
      <div className="header">
        <h2>Ease My Cure</h2>
        <div className="header-actions">
          <button
            className="header-button"
            onClick={() => setIsMaximized(!isMaximized)}
            title="Maximize/Restore"
          >
            &#x26F6;
          </button>
          <button
            className="header-button"
            onClick={() => setIsOpen(false)}
            title="Close"
          >
            &#x2715;
          </button>
          <div className="dropdown">
            <button className="dropdown-button">&#8942;</button>
            <div className="dropdown-content">
              <div className="session-info-dropdown">
                <strong>Session ID:</strong> {sessionId.replace('session_', '')}
                <br />
                <strong>User ID:</strong> {userId.replace('user_', '')}
              </div>
              <button onClick={resetSession}>Reset Session</button>
              <button onClick={resetUser}>Reset User</button>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="chat-container">
        <div className="chat-window" ref={chatWindowRef}>
          {messages.map((msg) => (
            <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
              {msg.audioUrl ? (
                <div className={`message-audio ${msg.sender}`}>
                  <button
                    className={`audio-play-button ${playingAudioId === msg.id ? 'playing' : ''}`}
                    onClick={() => playAudio(msg.audioUrl, msg.id)}
                    title={playingAudioId === msg.id ? 'Stop audio' : 'Play audio'}
                  >
                    {playingAudioId === msg.id ? '⏸️' : '▶️'}
                  </button>
                  <div className="audio-info">
                    <span className="audio-label">🎤 Audio Message</span>
                    <span className="audio-transcript">{msg.text}</span>
                  </div>
                </div>
              ) : (
                <div className={`message ${msg.sender}`}>
                  {msg.sender === 'bot' ? (
                    <div dangerouslySetInnerHTML={{ __html: marked(msg.text) }} />
                  ) : (
                    msg.text
                  )}
                </div>
              )}
            </div>
          ))}
          {isLoading && <div className="message bot loading">⏳ Processing...</div>}
        </div>

        {/* Input Area */}
        <div className="chat-input">
          <input
            type="text"
            placeholder="Type your message..."
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            disabled={isLoading || isRecording}
          />
          {!isRecording ? (
            <button onClick={sendMessage} disabled={isLoading || !userQuery.trim()}>
              Send
            </button>
          ) : null}
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isLoading}
            className={`mic-btn ${isRecording ? 'recording' : ''}`}
            title={isRecording ? 'Release to send audio' : 'Hold to record'}
            onMouseDown={!isRecording ? startRecording : null}
            onMouseUp={isRecording ? stopRecording : null}
            onTouchStart={!isRecording ? startRecording : null}
            onTouchEnd={isRecording ? stopRecording : null}
          >
            🎤
          </button>
        </div>
      </div>
    </div>
  );
};

export default VoiceChat;
