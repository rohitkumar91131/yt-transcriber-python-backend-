from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

app = Flask(__name__)
CORS(app)  # React Native ko server access allow karne ke liye

def extract_video_id(url):
    """
    YouTube URL se Video ID nikalne ka robust tareeka.
    """
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

# ==========================================
# 👇 YEH NAYA ROUTE ADD KIYA HAI (Home Page)
# ==========================================
@app.route('/', methods=['GET'])
def home():
    return """
    <h1>YT Transcriber API is Live! 🚀</h1>
    <p>Server mast chal raha hai.</p>
    <p>Use <b>/transcribe</b> endpoint for POST requests.</p>
    """

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "Bhai URL toh bhejo!"}), 400

    print(f"Processing URL: {video_url}")

    video_id = extract_video_id(video_url)
    
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
        full_text = " ".join([item['text'] for item in transcript_list])
        clean_text = full_text.replace('\n', ' ')
        
        return jsonify({"transcript": clean_text})

    except TranscriptsDisabled:
        return jsonify({"error": "Is video par subtitles disabled hain."}), 404
    except NoTranscriptFound:
        return jsonify({"error": "Is video ke liye English/Hindi transcript nahi mila."}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Server error aaya hai."}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)