from flask import Flask, request, jsonify
from flask_cors import CORS
# Change import style slightly to avoid some conflicts
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
import os

app = Flask(__name__)
CORS(app)

# 👇 DEBUGGING: Server start hote hi logs mein print karega ki library kahan se aa rahi hai
print("--- DEBUG INFO ---")
print(f"Library Location: {youtube_transcript_api.__file__}")
print(f"Library Attributes: {dir(YouTubeTranscriptApi)}")
print("------------------")

def extract_video_id(url):
    video_id = None
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        r'(?:embed\/)([0-9A-Za-z_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route('/', methods=['GET'])
def home():
    return "<h1>Server is Running with Debug Mode 🛠️</h1>"

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Processing URL: {video_url}")

    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        # Standard call
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
        
        full_text = " ".join([item['text'] for item in transcript_list])
        clean_text = full_text.replace('\n', ' ')
        
        return jsonify({"transcript": clean_text})

    except AttributeError as e:
        # Agar wahi error aaya, toh hum use pakad lenge
        print(f"CRITICAL ERROR: {e}")
        return jsonify({"error": "Library conflict detected. Check logs for file location."}), 500
        
    except TranscriptsDisabled:
        return jsonify({"error": "Subtitles are disabled for this video."}), 404
    except NoTranscriptFound:
        return jsonify({"error": "No English/Hindi transcript found."}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
