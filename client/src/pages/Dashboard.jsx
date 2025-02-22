import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send, Mic, MicOff } from 'lucide-react';
import { SpeechProvider, useSpeech } from './SpeechContext'; // Import the SpeechProvider and useSpeech hook

const GOOGLE_API_KEY = "AIzaSyCS3gGNqYkNRPpohC605xnRBS8t1dNt7q8";

function Dashboard() {
  const {
    startRecording,
    stopRecording,
    recording,
    message,
    onMessagePlayed,
    loading,
  } = useSpeech(); // Use the SpeechContext logic

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const sendMessage = async (content, type = 'text') => {
    if (!content && type === 'text') return;
    console.log("rerender")

    const newUserMessage = {
      id: Date.now(),
      content: type === 'text' ? content : "🎤 Voice message",
      sender: 'user',
      type,
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      let responseData;
      console.log("rerender")

      if (type === 'text') {
        const response = await axios.post(
          `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GOOGLE_API_KEY}`,
          { contents: [{ parts: [{ text: content }] }] }
        );
        responseData = response.data.candidates?.[0]?.content.parts?.[0]?.text || "I couldn't process that request.";
      } else if (type === 'audio') {
        // Send the audio file to the backend for transcription
        const formData = new FormData();
        formData.append('audio', content, 'recording.webm'); // Append the audio blob as a file

        const transcriptionResponse = await axios.post('http://127.0.0.1:5000/api/speech-to-text', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        if (transcriptionResponse.data.success) {
          const transcribedText = transcriptionResponse.data.text;
          // Update the placeholder message with the transcribed text
          setMessages((prevMessages) =>
            prevMessages.map((msg) =>
              msg.id === newUserMessage.id ? { ...msg, content: transcribedText } : msg
            )
          );
          return; // Exit early since the transcription is handled
        } else {
          responseData = "I couldn't transcribe the audio. Please try again.";
        }
      }

      if (responseData) {
        setMessages((prev) => [
          ...prev,
          { content: responseData },
        ]);
      }
    } catch (error) {
      console.error('Error processing request:', error);
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 1, content: "Error processing request.", sender: 'bot', type: 'text' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle new messages from the SpeechContext
  useEffect(() => {
    if (message) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), content: message, sender: 'bot', type: 'text' },
      ]);
      onMessagePlayed(); // Clear the current message in the SpeechContext
    }
  }, [message, onMessagePlayed]);

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="flex-1 p-4 overflow-y-auto">
  <div className="max-w-3xl mx-auto space-y-4">
    {messages.map((msg) => (
      <div key={msg.id}>
        {typeof msg.content === 'string' ? msg.content : (msg.content.content)}
      </div>
    ))}
  </div>
</div>


      <div className="w-full bg-white border-t p-4">
        <div className="max-w-3xl mx-auto flex gap-2 items-center">
          <Input
            className="flex-1"
            placeholder="Type a message..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            disabled={isLoading || recording}
          />

          <Button
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            disabled={isLoading || loading}
          >
            {recording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
          </Button>

          <Button
            onClick={() => sendMessage(inputMessage)}
            disabled={!inputMessage.trim() || isLoading || loading}
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}

// Wrap the Dashboard component with the SpeechProvider
export default function App() {
  return (
    <SpeechProvider>
      <Dashboard />
    </SpeechProvider>
  );
}