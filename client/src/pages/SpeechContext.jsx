import { createContext, useContext, useEffect, useState } from "react";

const backendUrl = "http://127.0.0.1:5000";

const SpeechContext = createContext();

export const SpeechProvider = ({ children }) => {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState();
  const [loading, setLoading] = useState(false);

  let chunks = [];

  const initiateRecording = () => {
    chunks = [];
  };

  const onDataAvailable = (e) => {
    chunks.push(e.data);
  };

  const convertWebMtoWAV = async (webmBlob) => {
    const audioContext = new AudioContext();
    const arrayBuffer = await webmBlob.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

    const wavBlob = encodeWAV(audioBuffer);
    return wavBlob;
  };

  const encodeWAV = (audioBuffer) => {
    const numChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const length = audioBuffer.length * numChannels * 2 + 44;
    const buffer = new ArrayBuffer(length);
    const view = new DataView(buffer);

    // Write WAV header
    writeString(view, 0, "RIFF");
    view.setUint32(4, 36 + audioBuffer.length * numChannels * 2, true); // File length
    writeString(view, 8, "WAVE");
    writeString(view, 12, "fmt ");
    view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
    view.setUint16(20, 1, true); // AudioFormat (1 for PCM)
    view.setUint16(22, numChannels, true); // NumChannels
    view.setUint32(24, sampleRate, true); // SampleRate
    view.setUint32(28, sampleRate * numChannels * 2, true); // ByteRate
    view.setUint16(32, numChannels * 2, true); // BlockAlign
    view.setUint16(34, 16, true); // BitsPerSample
    writeString(view, 36, "data");
    view.setUint32(40, audioBuffer.length * numChannels * 2, true); // Subchunk2Size

    // Write audio data
    const interleaved = interleave(audioBuffer);
    for (let i = 0; i < interleaved.length; i++) {
      view.setInt16(44 + i * 2, interleaved[i] * 0x7fff, true);
    }

    return new Blob([view], { type: "audio/wav" });
  };

  const interleave = (audioBuffer) => {
    const numChannels = audioBuffer.numberOfChannels;
    const length = audioBuffer.length * numChannels;
    const result = new Float32Array(length);

    for (let i = 0; i < audioBuffer.length; i++) {
      for (let channel = 0; channel < numChannels; channel++) {
        result[i * numChannels + channel] = audioBuffer.getChannelData(channel)[i];
      }
    }

    return result;
  };

  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  const sendAudioData = async (audioBlob) => {
    setLoading(true);
    try {
      const wavBlob = await convertWebMtoWAV(audioBlob); // Convert WebM to WAV
      const formData = new FormData();
      formData.append("audio", wavBlob, "recording.wav"); // Append WAV file
      console.log("rabcd")

      const response = await fetch(`${backendUrl}/api/speech-to-text`, {
        method: "POST",
        body: formData, // Send as multipart/form-data
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setMessages((messages) => [
          ...messages,
          { id: Date.now(), content: data.text, sender: "bot", type: "text" },
        ]);
      } else {
        throw new Error(data.error || "Failed to transcribe audio");
      }
      console.log(data)
    } catch (error) {
      console.error("Error sending audio data:", error);
      setMessages((messages) => [
        ...messages,
        { id: Date.now(), content: "Error transcribing audio.", sender: "bot", type: "text" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (typeof window !== "undefined") {
      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then((stream) => {
          const newMediaRecorder = new MediaRecorder(stream);
          newMediaRecorder.onstart = initiateRecording;
          newMediaRecorder.ondataavailable = onDataAvailable;
          newMediaRecorder.onstop = async () => {
            const audioBlob = new Blob(chunks, { type: "audio/webm" });
            try {
              await sendAudioData(audioBlob);
            } catch (error) {
              console.error(error);
              alert(error.message);
            }
          };
          setMediaRecorder(newMediaRecorder);
        })
        .catch((err) => console.error("Error accessing microphone:", err));
    }
  }, []);

  const startRecording = () => {
    if (mediaRecorder) {
        console.log("recording")

      mediaRecorder.start();
      setRecording(true);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setRecording(false);
    }
  };

  const onMessagePlayed = () => {
    setMessages((messages) => messages.slice(1));
  };

  useEffect(() => {
    if (messages.length > 0) {
      setMessage(messages[0]);
    } else {
      setMessage(null);
    }
  }, [messages]);

  return (
    <SpeechContext.Provider
      value={{
        startRecording,
        stopRecording,
        recording,
        message,
        onMessagePlayed,
        loading,
      }}
    >
      {children}
    </SpeechContext.Provider>
  );
};

export const useSpeech = () => {
  const context = useContext(SpeechContext);
  if (!context) {
    throw new Error("useSpeech must be used within a SpeechProvider");
  }
  return context;
};