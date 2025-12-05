# RAG Voice Chat Widget

A React-based voice chat interface for the RAG (Retrieval Augmented Generation) chatbot backend.

## Features

- 🎤 **Voice Input**: Record audio questions directly from your browser
- 🔊 **Audio Output**: Listen to AI-generated responses as speech
- 💬 **Text Transcript**: View the transcribed text of your question
- 🎨 **Modern UI**: Clean, responsive design with smooth animations
- ⚡ **Real-time Processing**: Get responses as you speak

## Installation

```bash
npm install
```

## Usage

1. Start your RAG backend server on `http://localhost:8000`
2. Start the React app:

```bash
npm start
```

3. Open `http://localhost:3000` in your browser
4. Click "🎤 Start Recording" to begin speaking
5. Click "⏹️ Stop Recording" when done
6. Wait for the response and listen to the AI's answer

## Configuration

To connect to a different backend URL, modify the `backendUrl` prop in `src/App.js`:

```javascript
<VoiceChat 
  sessionId={sessionId} 
  userId={userId}
  backendUrl="http://your-backend:8000"
/>
```

## API Endpoint

The component communicates with your backend's `/chat/audio` endpoint:

**Request:**
- Method: `POST`
- Headers: `Content-Type: multipart/form-data`
- Body:
  - `audio`: WAV audio file
  - `session_id`: Session identifier
  - `user_id`: User identifier

**Response:**
```json
{
  "text": "transcribed user question",
  "message": "AI response text",
  "audio_url": "/response_audio/filename.mp3"
}
```

## Tech Stack

- React 18
- Axios (HTTP client)
- Web Audio API (recording)
- CSS3 (styling & animations)

## Browser Support

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

Note: Requires HTTPS or localhost for microphone access.
