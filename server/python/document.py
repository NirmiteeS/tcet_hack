import streamlit as st
import google.generativeai as genai
import datetime
import time
import re
import os
import asyncio
from pathlib import Path
import logging
from googletrans import Translator, LANGUAGES
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import tempfile
import nest_asyncio
from typing import List, Optional, Any
import threading
import queue

# Enable nested event loops
nest_asyncio.apply()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Translation configuration
GTTS_LANG_CODES = {
    'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it', 'pt': 'pt',
    'ru': 'ru', 'hi': 'hi', 'ja': 'ja', 'ko': 'ko', 'zh-cn': 'zh-CN',
    'ar': 'ar', 'bn': 'bn', 'nl': 'nl', 'el': 'el', 'gu': 'gu', 'hu': 'hu',
    'id': 'id', 'kn': 'kn', 'ml': 'ml', 'mr': 'mr', 'ne': 'ne', 'pl': 'pl',
    'ta': 'ta', 'te': 'te', 'th': 'th', 'tr': 'tr', 'ur': 'ur', 'vi': 'vi'
}

class GeminiContextCache:
    def __init__(self):
        self.cached_models = {}
        self.MIN_TOKENS = 32768
        self.general_model = None
        self.translator = Translator()
        
        # Initialize API key from environment variable
        api_key ="AIzaSyCIGIFXMaYtlHanVHraamT8hFZH4RBL-_E"
        if api_key:
            self.setup_api(api_key)
        else:
            logger.error("GOOGLE_API_KEY not found in environment variables")

    def setup_api(self, api_key: str) -> bool:
        try:
            genai.configure(api_key=api_key)
            self.general_model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")
            return True
        except Exception as e:
            logger.error(f"Invalid API key: {str(e)}")
            return False

    def process_file(self, uploaded_file):
        try:
            temp_path = Path(f"temp_{uploaded_file.name}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            with st.status(f"Processing {uploaded_file.name}...", expanded=True) as status:
                try:
                    file_data = genai.upload_file(path=str(temp_path))
                    while file_data.state.name == "PROCESSING":
                        st.write("Processing...")
                        time.sleep(2)
                        file_data = genai.get_file(file_data.name)
                    status.update(label="Processing complete!", state="complete")
                except Exception as e:
                    status.update(label=f"Error: {str(e)}", state="error")
                    return None

            temp_path.unlink()
            return file_data
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None

    def create_padding_file(self) -> Optional[Any]:
        try:
            temp_path = Path("temp_padding.txt")
            padding_text = "This is padding content. " * 8000
            
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(padding_text)

            padding_data = genai.upload_file(path=str(temp_path))
            while getattr(padding_data, 'state', None) and padding_data.state.name == "PROCESSING":
                time.sleep(1)
                padding_data = genai.get_file(padding_data.name)
            
            temp_path.unlink()
            return padding_data
        except Exception as e:
            st.error(f"Error creating padding: {str(e)}")
            return None

    def update_cache(self, new_files: List, cache_name: str, 
                    system_instruction: str, ttl_minutes: int) -> Optional[str]:
        try:
            processed_files = []
            for uploaded_file in new_files:
                file_data = self.process_file(uploaded_file)
                if file_data:
                    processed_files.append(file_data)

            if not processed_files:
                st.error("No files were successfully processed.")
                return None

            existing_cache = self.cached_models.get(cache_name)
            if existing_cache:
                all_files = existing_cache.cached_content.contents + processed_files
            else:
                all_files = processed_files

            max_retries = 2
            for attempt in range(max_retries):
                try:
                    cache = genai.caching.CachedContent.create(
                        model="models/gemini-1.5-flash-001",
                        display_name=cache_name,
                        system_instruction=system_instruction,
                        contents=all_files,
                        ttl=datetime.timedelta(minutes=ttl_minutes)
                    )
                    
                    self.cached_models[cache_name] = genai.GenerativeModel.from_cached_content(
                        cached_content=cache
                    )
                    return cache_name
                    
                except Exception as e:
                    if "Cached content is too small" in str(e) and attempt < max_retries - 1:
                        st.warning("Adding padding content...")
                        padding_data = self.create_padding_file()
                        if padding_data:
                            all_files.append(padding_data)
                        continue
                    else:
                        st.error(f"Error updating cache: {str(e)}")
                        return None
        except Exception as e:
            st.error(f"Error in update_cache: {str(e)}")
            return None

    def query_model(self, prompt: str, chat_history: list, use_files: bool = False) -> dict:
        try:
            if prompt.strip().lower().startswith('translate'):
                return self.handle_translation(prompt)
                
            gemini_history = []
            for msg in chat_history[:-1]:
                if msg["role"] == "user":
                    gemini_history.append({"role": "user", "parts": [{"text": msg["content"]}]})
                elif msg["role"] == "assistant":
                    gemini_history.append({"role": "model", "parts": [{"text": msg["content"]}]})
            
            if use_files and st.session_state.current_cache in self.cached_models:
                model = self.cached_models[st.session_state.current_cache]
                prompt_with_context = f"""Using the context from the uploaded files ({st.session_state.current_cache}), answer:

{prompt}

Reference specific file contents where applicable. If unsure, state that information isn't available."""
            else:
                model = self.general_model
                prompt_with_context = prompt

            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(prompt_with_context)
            
            return {'text': response.text, 'audio_path': None}

        except Exception as e:
            error_msg = f"Error getting response: {str(e)}"
            st.error(error_msg)
            return {'text': error_msg, 'audio_path': None}
        
    def run_async(self, coroutine):
        """Helper method to run async code in sync context"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coroutine)

    async def async_translate(self, text, dest_lang):
        """Async method to handle translation"""
        detected = await self.translator.detect(text)
        translated = await self.translator.translate(text, dest=dest_lang)
        return detected, translated

    def handle_translation(self, prompt: str) -> dict:
        try:
            # Parse translation request
            remaining = prompt[len('translate'):].strip()
            if ' to ' in remaining:
                text_part, lang_part = remaining.rsplit(' to ', 1)
                text_to_translate = text_part.strip().strip('"')
                target_lang = lang_part.strip()
            else:
                text_to_translate = remaining.strip('"')
                target_lang = st.session_state.get('target_lang', 'en')

            # Map target language to code
            lang_code = None
            for code, name in LANGUAGES.items():
                if target_lang.lower() in [name.lower(), code.lower()]:
                    lang_code = code
                    break
            lang_code = lang_code or 'en'

            # Run translation in sync context
            detected, translated = self.run_async(
                self.async_translate(text_to_translate, lang_code)
            )
            
            # Generate TTS if enabled
            audio_path = None
            if st.session_state.get('enable_tts', False) and lang_code in GTTS_LANG_CODES:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    tts = gTTS(translated.text, lang=GTTS_LANG_CODES[lang_code])
                    tts.save(tmp_file.name)
                    audio_path = tmp_file.name
                    st.session_state.temp_files.append(audio_path)

            return {
                'text': f"Detected Language: {LANGUAGES.get(detected.lang, 'Unknown')}\n\nTranslation: {translated.text}",
                'audio_path': audio_path
            }
        except Exception as e:
            logger.error(f"Translation error details: {str(e)}", exc_info=True)
            return {'text': f"Translation error: {str(e)}", 'audio_path': None}

def recognize_speech(audio_file):
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
        return r.recognize_google(audio)
    except Exception as e:
        st.error(f"Speech recognition error: {str(e)}")
        return None

def safe_delete(file_path):
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.warning(f"Could not delete file {file_path}: {str(e)}")

def record_audio(audio_queue: queue.Queue, stop_recording: threading.Event):
    """Record audio in a separate thread until stop signal is received"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while not stop_recording.is_set():
            try:
                audio = r.listen(source, phrase_time_limit=None)
                audio_queue.put(audio)
            except Exception as e:
                logger.error(f"Error recording audio: {e}")
                break

def main():
    st.set_page_config(
        page_title="AI Assistant with Speech & Translation",
        layout="wide"
    )
    
    # Initialize session state
    if 'cache' not in st.session_state:
        st.session_state.cache = GeminiContextCache()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'temp_files' not in st.session_state:
        st.session_state.temp_files = []
    if 'target_lang' not in st.session_state:
        st.session_state.target_lang = 'en'
    if 'current_cache' not in st.session_state:
        st.session_state.current_cache = None
    if 'system_instruction' not in st.session_state:
        st.session_state.system_instruction = "Analyze the provided files and answer questions about them."
    if 'ttl_minutes' not in st.session_state:
        st.session_state.ttl_minutes = 10

    # Sidebar configuration (keep previous file and translation settings)
    with st.sidebar:
        # st.header("Configuration")
        # if st.session_state.cache.general_model:
        #     st.success("API Configured from environment variables!")
        # else:
        #     st.error("API key not found. Please set GOOGLE_API_KEY in your .env file")

        st.header("File Management")
        uploaded_files = st.file_uploader(
            "Upload files for context",
            accept_multiple_files=True,
            type=['txt', 'pdf', 'docx', 'doc', 'jpg', 'png', 'mp4']
        )
        
        if uploaded_files:
            cache_name = st.text_input("Cache Name", 
                                     value=f"cache_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
            st.session_state.system_instruction = st.text_area(
                "System Instruction",
                value=st.session_state.system_instruction
            )
            st.session_state.ttl_minutes = st.number_input(
                "Cache Duration (minutes)", 
                min_value=1, 
                max_value=60, 
                value=10
            )
            
            if st.button("Process Files"):
                st.session_state.current_cache = st.session_state.cache.update_cache(
                    uploaded_files,
                    cache_name,
                    st.session_state.system_instruction,
                    st.session_state.ttl_minutes
                )
                if st.session_state.current_cache:
                    st.success(f"Using cache: {st.session_state.current_cache}")

        # st.header("Translation Settings")
        # st.session_state.target_lang = st.selectbox(
        #     "Target Language",
        #     options=list(LANGUAGES.keys()),
        #     format_func=lambda x: f"{x} - {LANGUAGES[x]}"
        # )
        st.session_state.enable_tts = st.checkbox("Enable Text-to-Speech")

    # Main interface
    st.title("AI Assistant with Speech & Translation")
    
    # Chat container
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("audio"):
                    st.audio(msg["audio"], format="audio/mp3")


    # Input container with voice recording
    if 'is_recording' not in st.session_state:
        st.session_state.is_recording = False
    if 'audio_thread' not in st.session_state:
        st.session_state.audio_thread = None
    if 'stop_recording' not in st.session_state:
        st.session_state.stop_recording = threading.Event()
    if 'audio_queue' not in st.session_state:
        st.session_state.audio_queue = queue.Queue()

    with st.container():
        col1, col2 = st.columns([4, 1])

        with col1:
            prompt = st.chat_input("Type or speak your message...")

        with col2:
            if not st.session_state.cache.general_model:
                st.button("🎤 Record", disabled=True, help="Please configure API key first")
            else:
                button_text = "🛑 Stop Recording" if st.session_state.is_recording else "🎤 Start Recording"
                if st.button(button_text):
                    if not st.session_state.is_recording:
                        # Start recording
                        st.session_state.is_recording = True
                        st.session_state.stop_recording.clear()
                        st.session_state.audio_queue = queue.Queue()
                        st.session_state.audio_thread = threading.Thread(
                            target=record_audio,
                            args=(st.session_state.audio_queue, st.session_state.stop_recording)
                        )
                        st.session_state.audio_thread.start()
                        st.info("Recording started... Press the button again to stop.")
                        st.rerun()
                    else:
                        # Stop recording and process audio
                        st.session_state.stop_recording.set()
                        if st.session_state.audio_thread:
                            st.session_state.audio_thread.join()
                        
                        # Process all audio segments
                        full_text = []
                        while not st.session_state.audio_queue.empty():
                            audio = st.session_state.audio_queue.get()
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                                tmp_file.write(audio.get_wav_data())
                                audio_path = tmp_file.name
                                st.session_state.temp_files.append(audio_path)
                                
                                try:
                                    text = recognize_speech(audio_path)
                                    if text:
                                        full_text.append(text)
                                except Exception as e:
                                    st.error(f"Error processing audio segment: {str(e)}")
                        
                        if full_text:
                            combined_text = " ".join(full_text)
                            st.session_state.chat_history.append({"role": "user", "content": combined_text})
                        
                        # Reset recording state
                        st.session_state.is_recording = False
                        st.rerun()
      

    # Handle text input
    if prompt:
        if not st.session_state.cache.general_model:
            st.error("Please configure your API key in the sidebar first")
        else:
            st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Response generation (keep previous response handling)
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        user_input = st.session_state.chat_history[-1]["content"]
        
        with st.spinner("Processing..."):
            use_files = any(keyword in user_input.lower() for keyword in ['file', 'document', 'page'])
            response = st.session_state.cache.query_model(
                user_input, 
                st.session_state.chat_history,
                use_files=use_files or bool(st.session_state.current_cache))
            
            if response['text']:
                response_data = {"role": "assistant", "content": response['text']}
                st.session_state.chat_history.append(response_data)
                st.rerun()
    # Cleanup
    for file in st.session_state.temp_files:
        safe_delete(file)
    st.session_state.temp_files = []

if __name__ == "__main__":
    main()