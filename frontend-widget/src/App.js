import React from 'react';
import VoiceChat from './components/VoiceChat';
import './App.css';

function App() {
  const sessionId = 'session_' + Date.now();
  const userId = 'user_demo';

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎙️ RAG Chatbot - Voice Interface</h1>
        <p>Ask healthcare questions using your voice</p>
      </header>
      <VoiceChat 
        sessionId={sessionId} 
        userId={userId}
        backendUrl="http://localhost:8000"
      />
    </div>
  );
}

export default App;
