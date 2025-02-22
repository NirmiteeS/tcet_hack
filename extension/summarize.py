import customtkinter as ctk
from tkinter import filedialog, messagebox
import google.generativeai as genai
from google.cloud import speech_v1p1beta1 as speech
import os

# Configure Gemini API (replace with your API key)
genai.configure(api_key="AIzaSyC5kiR_7pP0x1ft-Fd2mqgakXwl_D7-Kl0")

# Initialize Gemini model
model = genai.GenerativeModel('gemini-pro')

# Function to transcribe audio/video using Google Speech-to-Text
def transcribe_audio_video(file_path):
    try:
        # Initialize the Speech-to-Text client
        client = speech.SpeechClient()

        # Read the audio file
        with open(file_path, "rb") as audio_file:
            content = audio_file.read()

        # Configure the audio file
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",  # Change language code as needed
        )

        # Transcribe the audio
        response = client.recognize(config=config, audio=audio)

        # Extract and return the transcribed text
        transcribed_text = ""
        for result in response.results:
            transcribed_text += result.alternatives[0].transcript + " "

        return transcribed_text.strip()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to transcribe file: {e}")
        return None

# Function to summarize text using Gemini API
def summarize_text_with_gemini(text):
    try:
        # Prompt for summarization
        prompt = f"""Summarize the following text in a concise and engaging way. Use bullet points, emojis, and make it visually appealing:
        {text}"""

        # Generate summary
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        messagebox.showerror("Error", f"Failed to summarize text: {e}")
        return None

# Function to handle file upload and summarization
def upload_file():
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("Audio Files", "*.mp3 *.wav"), ("Video Files", "*.mp4 *.avi")]
    )
    if file_path:
        # Transcribe the file
        transcribed_text = transcribe_audio_video(file_path)
        if transcribed_text:
            # Summarize the transcribed text
            summarized_text = summarize_text_with_gemini(transcribed_text)
            if summarized_text:
                # Display the summarized text in a new window
                display_summary(summarized_text)

# Function to display the summarized text in a new window
def display_summary(summarized_text):
    summary_window = ctk.CTkToplevel()
    summary_window.title("Summary")
    summary_window.geometry("600x400")

    # Add a label for the summary
    label = ctk.CTkLabel(summary_window, text="📝 Summary", font=("Arial", 16))
    label.pack(pady=10)

    # Add a textbox to display the summary
    textbox = ctk.CTkTextbox(summary_window, width=550, height=300, font=("Arial", 12))
    textbox.insert("1.0", summarized_text)
    textbox.configure(state="disabled")  # Make it read-only
    textbox.pack(pady=10, padx=10)

    # Close button
    close_btn = ctk.CTkButton(summary_window, text="Close", command=summary_window.destroy, corner_radius=8)
    close_btn.pack(pady=10)

# Create the summarizer window
def create_summarize_window():
    summarize_window = ctk.CTkToplevel()
    summarize_window.title("Summarizer")
    summarize_window.geometry("500x300")

    # Label for the summarizer window
    label = ctk.CTkLabel(summarize_window, text="Upload Audio/Video for Summarization", font=("Arial", 16))
    label.pack(pady=20)

    # File Upload Button
    upload_btn = ctk.CTkButton(summarize_window, text="Upload File", command=upload_file, corner_radius=8)
    upload_btn.pack(pady=20)

    # Close button to exit the summarizer window
    close_btn = ctk.CTkButton(summarize_window, text="Close", command=summarize_window.destroy, corner_radius=8)
    close_btn.pack(pady=20)