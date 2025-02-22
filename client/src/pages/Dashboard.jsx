import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send, Mic, MicOff, User, Bot, Paperclip, Pencil } from 'lucide-react';
import { SpeechProvider, useSpeech } from './SpeechContext';
import axios from 'axios';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

const GOOGLE_API_KEY = "AIzaSyCS3gGNqYkNRPpohC605xnRBS8t1dNt7q8";

const DocCard = ({ title, thumbnail, link }) => (
  <div 
    onClick={() => window.open(link, '_blank')}
    className="flex items-center p-4 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors duration-200"
  >
    <div className="flex-shrink-0">
      <img src={"https://drive-thirdparty.googleusercontent.com/128/type/application/vnd.google-apps.document"} alt={title} className="w-16 h-16 object-cover rounded" />
    </div>
    <div className="ml-4 flex-grow">
      <h4 className="text-sm font-medium text-gray-900">{title}</h4>
      <p className="text-xs text-gray-500">Click to open document</p>
    </div>
  </div>
);

const MessageBubble = ({ message, isUser }) => (
  <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
    <div className={`flex items-start gap-2.5 ${isUser ? 'flex-row-reverse' : 'flex-row'} max-w-[80%]`}>
      <div className={`flex items-center justify-center w-8 h-8 rounded-full ${isUser ? 'bg-blue-500' : 'bg-gray-600'}`}>
        {isUser ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
      </div>
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`p-3 rounded-lg ${isUser ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-900'}`}>
          {message.type === 'doc' ? (
            <DocCard 
              title={message.docInfo.title}
              thumbnail={message.docInfo.thumbnail}
              link={message.docInfo.link}
            />
          ) : (
            <p className="text-sm">{typeof message.content === 'string' ? message.content : message.content.content}</p>
          )}
        </div>
      </div>
    </div>
  </div>
);

function Dashboard() {
  const {
    startRecording,
    stopRecording,
    recording,
    message,
    onMessagePlayed,
    loading,
  } = useSpeech();

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [docTitle, setDocTitle] = useState('');
  const [docContent, setDocContent] = useState('');
  const fileInputRef = React.useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const sendMessage = async (content, type = 'text') => {
    if (!content && type === 'text') return;

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

      if (/create\s+\w*\s*google\s+\w*\s*doc\w*/i.test(content)) {
        setIsModalOpen(true);
        return;
      }

      if (/upload\s+\w*\s*doc\w*/i.test(content)) {
        if (selectedFile) {
          const filePath = selectedFile.name; // Using filename as path
          const mimeType = selectedFile.type || 'application/octet-stream';
          await uploadOnGoogleDrive(filePath, mimeType);
          setSelectedFile(null);
          setMessages(prev => [...prev, {
            id: Date.now(),
            content: `Uploaded file: ${filePath}`,
            sender: 'bot',
            type: 'text'
          }]);
        }
        return;
      }   

      if (/schedule a meet|schedule a meeting/i.test(content)) {
        try {
          const response = await axios.post('http://localhost:8000/schedule', { text: content });
          responseData = response.data.message;
        } catch (error) {
          console.error('Error scheduling meeting:', error);
          responseData = 'Failed to schedule meeting. Please try again.';
        }
      } else if (type === 'text') {
        const response = await axios.post(
          `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GOOGLE_API_KEY}`,
          { contents: [{ parts: [{ text: content }] }] }
        );
        responseData = response.data.candidates?.[0]?.content.parts?.[0]?.text || "I couldn't process that request.";
      } else if (type === 'audio') {
        const formData = new FormData();
        formData.append('audio', content, 'recording.webm');

        const transcriptionResponse = await axios.post('http://127.0.0.1:5000/api/speech-to-text', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        if (transcriptionResponse.data.success) {
          const transcribedText = transcriptionResponse.data.text;
          setMessages((prevMessages) =>
            prevMessages.map((msg) =>
              msg.id === newUserMessage.id ? { ...msg, content: transcribedText } : msg
            )
          );
          return;
        } else {
          responseData = "I couldn't transcribe the audio. Please try again.";
        }
      }

      if (responseData) {
        setMessages((prev) => [
          ...prev,
          { id: Date.now() + 1, content: responseData, sender: 'bot', type: 'text' },
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

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputMessage);
    }
  };

  useEffect(() => {
    if (message) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), content: message, sender: 'bot', type: 'text' },
      ]);
      onMessagePlayed();
    }
  }, [message, onMessagePlayed]);

  const createGoogleDoc = async (title, content) => {
    const response = await axios.post("http://127.0.0.1:8000/create_google_doc", {
      title,
      content,
    });

    return response;
  }

  const uploadOnGoogleDrive = async (file_path, mime_type) => {
    const response = await axios.post("http://127.0.0.1:8000/upload_to_drive", {
      file_path,
      mime_type,
    })

    console.log(response.data);
  }

  const handleCreateDoc = async (e) => {
    e.preventDefault();
    const response = await createGoogleDoc(docTitle, docContent);
    console.log(response.data.thumbnail);
    setIsModalOpen(false);
    setDocTitle('');
    setDocContent('');
    
    // Add success message with doc info
    setMessages(prev => [...prev, {
      id: Date.now(),
      content: `Created Google Doc: ${docTitle}`,
      sender: 'bot',
      type: 'text'
    }, {
      id: Date.now() + 1,
      docInfo: {
        title: response.data.title,
        thumbnail: response.data.thumbnail,
        link: response.data.link
      },
      sender: 'bot',
      type: 'doc'
    }]);
  };

  const handleFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setInputMessage(`upload doc ${file.name}`);
    }
  };

  const [isComposeOpen, setIsComposeOpen] = useState(false);

  return (
    <div className="flex flex-col h-screen bg-white">
      {/* Chat Header */}
      <div className="border-b p-4 bg-gray-700 text-white">
        <h1 className="text-xl font-semibold text-center ">AI Chat Assistant for Google suite</h1>
      </div>

      <Button
        onClick={() => setIsComposeOpen(true)}
        className="fixed bottom-10 right-6 bg-blue-500 text-white p-4 rounded-full shadow-lg hover:bg-blue-600"
      >
        <Pencil className="w-5 h-5" />
      </Button>


      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-3xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-8">
              <p className="text-lg">👋 Welcome! How can I help you today?</p>
            </div>
          )}
          {messages.map((msg) => (
            <MessageBubble 
              key={msg.id} 
              message={msg} 
              isUser={msg.sender === 'user'}
            />
          ))}
          {isLoading && (
            <div className="flex items-center space-x-2 text-gray-500">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t p-4 bg-white">
        <div className="max-w-3xl mx-auto">
          <div className="relative flex items-center gap-2">
            <Input
              className="flex-1 p-3 pr-12 rounded-lg border focus:ring-2 focus:ring-blue-500 text-black"
              placeholder="Type a message..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading || recording}
              rows={1}
            />
            <div className="flex gap-2">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
              />
              <Button
                variant="outline"
                size="icon"
                onClick={handleFileClick}
                className="rounded-full"
              >
                <Paperclip className="h-5 w-5" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onMouseDown={startRecording}
                onMouseUp={stopRecording}
                disabled={isLoading || loading}
                className="rounded-full"
              >
                {recording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </Button>
              <Button
                onClick={() => sendMessage(inputMessage)}
                disabled={!inputMessage.trim() || isLoading || loading}
                className="rounded-full"
              >
                <Send className="h-5 w-5" />
              </Button>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send, Shift + Enter for new line
          </p>
        </div>
      </div>
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Create New Google Doc</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleCreateDoc}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="title" className="text-right">
                  Title
                </Label>
                <Input
                  id="title"
                  value={docTitle}
                  onChange={(e) => setDocTitle(e.target.value)}
                  className="col-span-3"
                  required
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="content" className="text-right">
                  Content
                </Label>
                <Textarea
                  id="content"
                  value={docContent}
                  onChange={(e) => setDocContent(e.target.value)}
                  className="col-span-3"
                  required
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit">Create Doc</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      {/* Compose Model */}
      <Dialog open={isComposeOpen} onOpenChange={setIsComposeOpen}>
        <DialogContent className="sm:max-w-[600px] -p-6">
          <div className="w-full h-[600px]">
            <iframe
              src="http://localhost:8504" 
              className="w-full h-full border rounded-lg"
            />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default function App() {
  return (
    <SpeechProvider>
      <Dashboard />
    </SpeechProvider>
  );
}