import os
import sys
import time
import webbrowser
import pyautogui
import pandas as pd
import subprocess
import speech_recognition as sr
import customtkinter as ctk

def create_audio_text_window():
    """Creates the audio-text window."""
    window = ctk.CTkToplevel()
    window.title("Audio to Text / Text to Audio")
    window.geometry("400x300")

    label = ctk.CTkLabel(window, text="Audio-Text Functionality", font=("Arial", 16))
    label.pack(pady=20)

    button = ctk.CTkButton(window, text="Convert Audio to Text", command=lambda: print("Converting Audio to Text..."))
    button.pack(pady=10)

    button2 = ctk.CTkButton(window, text="Convert Text to Audio", command=lambda: print("Converting Text to Audio..."))
    button2.pack(pady=10)

    window.mainloop()

# Load command mappings from CSV
commands_file = "commands.csv"
commands_df = pd.read_csv(commands_file)
commands_dict = dict(zip(commands_df["command"], commands_df["action"]))

recognizer = sr.Recognizer()
typing_mode = False  # Track typing mode
notepad_open = False  # Track if Notepad is open

def listen():
    """ Listen for voice commands """
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10)
            command = recognizer.recognize_google(audio).lower()
            print(f"Recognized command: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand the command.")
        except sr.RequestError:
            print("Speech Recognition service error.")
        except sr.WaitTimeoutError:
            print("Listening timed out.")
        return None

def search_google():
    """ Wait for search query and search Google in the current tab """
    print("What do you want to search for?")
    query = listen()  # Wait for the voice input
    if query:
        print(f"Searching Google for: {query}")
        
        try:
            # Open Google in the default browser
            webbrowser.open("https://www.google.com")
            time.sleep(2)  # Wait for the browser to open and load Google

            # Focus the browser window (may require additional steps depending on the OS)
            pyautogui.hotkey('alt', 'tab')  # Switch to the browser window
            time.sleep(1)  # Wait for the window to focus

            # Simulate typing the search query in the search bar and pressing Enter
            pyautogui.write(query)
            time.sleep(1)  # Wait for typing to complete
            pyautogui.press('enter')  # Press Enter to perform the search
        except Exception as e:
            print(f"Error while searching: {e}")
    else:
        print("Could not understand the search query.")

def close_window():
    """ Close the active window """
    pyautogui.hotkey("alt", "f4")

def execute_typing(command):
    """ Handle typing commands in Notepad """
    global typing_mode

    if command == "stop typing":
        typing_mode = False
        print("Typing mode deactivated.")
        return

    elif command == "enter":
        pyautogui.press("enter")

    elif command == "backspace":
        pyautogui.press("backspace")

    elif command == "space":
        pyautogui.press("space")

    else:
        pyautogui.write(command)

def execute_command(command):
    """ Execute corresponding action from CSV """
    global typing_mode, notepad_open

    if not command:
        print("Command not recognized.")
        return

    action = commands_dict.get(command)

    if action:
        if action == "start_typing":
            typing_mode = True
            print("Typing mode activated. Say 'Stop Typing' to exit.")
            while typing_mode:
                print("Listening for typing commands...")
                command = listen()
                if command:
                    execute_typing(command)
            return

        elif action == "stop_typing":
            typing_mode = False
            print("Typing mode deactivated.")
            return

        elif action.startswith("web "):  
            url = action.replace("web ", "").strip()
            webbrowser.open(url)
            print(f"Opened: {url}")

        elif action == "search_google":
            search_google()

        elif action == "close_window":
            close_window()

        elif action == "stop_voice":
            print("Stopping voice command system.")
            sys.exit()

        elif action.startswith("app "):  
            app_name = action.replace("app ", "").strip()
            try:
                subprocess.Popen(app_name, shell=True)
                print(f"Opened: {app_name}")
                if app_name.lower() == "notepad":
                    notepad_open = True  
                    time.sleep(1)  # Wait for Notepad to open
                    pyautogui.hotkey('alt', 'tab')  # Bring Notepad to the foreground
            except Exception as e:
                print(f"Error opening {app_name}: {e}")

        else:
            try:
                os.system(action)
                print(f"Executed: {action}")
            except Exception as e:
                print(f"Error executing command: {e}")

    else:
        print("Command not recognized.")

def main():
    """ Main loop for voice command execution """
    while True:
        command = listen()
        execute_command(command)

if __name__ == "__main__":
    print("Listening for commands...")
    main()
