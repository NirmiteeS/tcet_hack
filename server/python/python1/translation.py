from flask import Flask, request, jsonify, send_file
from googletrans import Translator, LANGUAGES
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
from pathlib import Path
import asyncio
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

GTTS_LANG_CODES = {
    'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it', 'pt': 'pt',
    'ru': 'ru', 'hi': 'hi', 'ja': 'ja', 'ko': 'ko', 'zh-cn': 'zh-CN',
    'ar': 'ar', 'bn': 'bn', 'nl': 'nl', 'el': 'el', 'gu': 'gu', 'hu': 'hu',
    'id': 'id', 'kn': 'kn', 'ml': 'ml', 'mr': 'mr', 'ne': 'ne', 'pl': 'pl',
    'ta': 'ta', 'te': 'te', 'th': 'th', 'tr': 'tr', 'ur': 'ur', 'vi': 'vi'
}

def async_route(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapped

def safe_delete(file_path):
    """Safely delete a file if it exists."""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Could not delete temporary file: {file_path}")

def recognize_speech(audio_file):
    """Convert audio file to text using speech recognition."""
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        return text
    except Exception as e:
        return None

async def translate_text(sentence, dest_lang):
    """Async function to handle translation."""
    if not sentence:
        return None
        
    trans = Translator()
    try:
        detection = await trans.detect(sentence)
        detected_lang = detection.lang
        
        trans_sen = await trans.translate(sentence, src=detected_lang, dest=dest_lang)
        return {
            'detected_language': LANGUAGES.get(detected_lang, 'Unknown'),
            'translated_text': trans_sen.text
        }
    except Exception as e:
        return None

@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    """
    Endpoint to convert speech to text
    Expects: audio file in WAV format
    Returns: JSON with recognized text
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            audio_file.save(tmp_file.name)
            recognized_text = recognize_speech(tmp_file.name)
            safe_delete(tmp_file.name)

            if recognized_text:
                return jsonify({
                    'success': True,
                    'text': recognized_text
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Could not recognize speech'
                }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/translate', methods=['POST'])
@async_route
async def translate():
    """
    Endpoint to translate text
    Expects: JSON with text and target language
    Returns: JSON with translation
    """
    data = request.get_json()
    if not data or 'text' not in data or 'target_language' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400

    text = data['text']
    target_lang = data['target_language']

    if target_lang not in LANGUAGES:
        return jsonify({'error': 'Invalid target language'}), 400

    result = await translate_text(text, target_lang)
    
    if result:
        return jsonify({
            'success': True,
            'translation': result
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Translation failed'
        }), 500

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """
    Endpoint to convert text to speech
    Expects: JSON with text and language code
    Returns: Audio file
    """
    data = request.get_json()
    if not data or 'text' not in data or 'language' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400

    text = data['text']
    lang_code = data['language']

    if lang_code not in GTTS_LANG_CODES:
        return jsonify({'error': 'Language not supported for text-to-speech'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts = gTTS(text=text, lang=GTTS_LANG_CODES[lang_code])
            tts.save(tmp_file.name)
            
            response = send_file(
                tmp_file.name,
                mimetype='audio/mp3',
                as_attachment=True,
                download_name='translation.mp3'
            )
            
            # Delete file after sending
            @response.call_on_close
            def cleanup():
                safe_delete(tmp_file.name)

            return response

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)