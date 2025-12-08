import React from 'react';
import VoiceChat from './components/VoiceChat';
import './App.css';

function App() {
  return (
    <div className="App">
      <VoiceChat 
        sessionId={'session_' + Date.now()} 
        userId={'user_' + Date.now()}
        backendUrl="http://localhost:8000"
      />
    </div>
  );
}

export default App;
