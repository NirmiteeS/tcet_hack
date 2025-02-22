import customtkinter as ctk
import threading
from tkinter import messagebox  # Import messagebox for displaying messages
from audio_text import create_audio_text_window  # Import the new function for audio-text window
import voice_command  # Import the voice_command module
import summarize  # Import the summarize module

# Function to run voice command in a separate thread
def run_voice_command():
    """Start the voice command system in a separate thread."""
    try:
        # Start the voice command system in a new thread
        voice_thread = threading.Thread(target=voice_command.main)
        voice_thread.daemon = True  # Ensure the thread exits when the main program exits
        voice_thread.start()
        messagebox.showinfo("Voice Command", "Voice command system started. Say 'stop voice' to exit.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start voice command system: {e}")

# Function to run summarizer
def run_summarize_text():
    """Open the summarizer window."""
    try:
        # Open the summarizer window
        summarize.create_summarize_window()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open summarizer: {e}")

# Create GUI
def create_window():
    """Create the main GUI window."""
    window = ctk.CTk()
    window.title("Desktop Extension")
    window.geometry("400x300")

    sidebar = ctk.CTkFrame(window, width=120, height=300, corner_radius=10)
    sidebar.pack(side="left", fill="y", padx=10, pady=10)

    # Voice Command Button
    btn1 = ctk.CTkButton(sidebar, text="Voice Command", command=run_voice_command, corner_radius=8)
    btn1.pack(pady=10, padx=10)

    # Audio-Text Button (calls the audio-to-text or text-to-audio functionality)
    btn2 = ctk.CTkButton(sidebar, text="Audio-Text", command=create_audio_text_window, corner_radius=8)
    btn2.pack(pady=10, padx=10)

    # Summarizer Button (calls the summarizer functionality)
    btn3 = ctk.CTkButton(sidebar, text="Summarizer", command=run_summarize_text, corner_radius=8)
    btn3.pack(pady=10, padx=10)

    # Label for the main window
    label = ctk.CTkLabel(window, text="Desktop Extension", font=("Arial", 16))
    label.pack(pady=20)

    # Close button to exit the application
    close_btn = ctk.CTkButton(window, text="Close", command=window.destroy, corner_radius=8)
    close_btn.pack(pady=20)

    window.mainloop()

# Only run the GUI if this file is executed directly
if __name__ == "__main__":
    create_window()