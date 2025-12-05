import React, { useState, useRef } from 'react';
import axios from 'axios';
import './VoiceChat.css';

const VoiceChat = ({ sessionId, userId, backendUrl = 'http://localhost:8000' }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [error, setError] = useState('');
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

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
    } catch (error) {
      setError('Microphone access denied. Please allow microphone permissions.');
      console.error('Microphone access denied:', error);
    }
  };

  const stopRecording = async () => {
    if (!mediaRecorderRef.current) return;

    mediaRecorderRef.current.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
      await sendAudio(audioBlob);
      setIsRecording(false);
    };

    mediaRecorderRef.current.stop();
    mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
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

      console.log('API Response:', res.data);
      console.log('Audio URL from API:', res.data.audio_url);
      
      setTranscript(res.data.text);
      setResponse(res.data.message);
      
      // Construct the full audio URL
      const fullAudioUrl = res.data.audio_url && res.data.audio_url.trim() 
        ? (res.data.audio_url.startsWith('http') 
            ? res.data.audio_url 
            : `${backendUrl}${res.data.audio_url}`)
        : '';
      
      console.log('Full audio URL:', fullAudioUrl);
      setAudioUrl(fullAudioUrl);
    } catch (error) {
      console.error('Error sending audio:', error);
      setError('Error processing audio. Please check if backend is running and try again.');
      setResponse('');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="voice-chat-container">
      <button 
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isLoading}
        className={`record-btn ${isRecording ? 'recording' : ''}`}
      >
        {isRecording ? '⏹️ Stop Recording' : '🎤 Start Recording'}
      </button>

      {isLoading && <p className="loading">⏳ Processing your audio...</p>}

      {error && <p className="error">❌ {error}</p>}

      {transcript && (
        <div className="transcript">
          <strong>👤 You said:</strong>
          <p>{transcript}</p>
        </div>
      )}

      {response && (
        <div className="response">
          <strong>🤖 Response:</strong>
          <p>{response}</p>
        </div>
      )}

      {audioUrl && (
        <div className="audio-player">
          <strong>🔊 Listen to response:</strong>
          <audio controls style={{width: '100%'}}>
            <source src={audioUrl} type="audio/mpeg" />
            <source src={audioUrl} type="audio/wav" />
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  );
};

export default VoiceChat;
