from flask import Flask, request, jsonify
from flask_cors import CORS
# Note: Hum naye tarike se import kar rahe hain
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

app = Flask(__name__)
CORS(app)

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
    return "<h1>YT Transcriber API is Live! (v2.0) 🚀</h1>"

@app.route('/transcribe', methods=['POST'])
def transcribe_video():
    data = request.json
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "URL missing"}), 400

    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        # 👇 MAGIC FIX: Naye version mein hume Pehle Class banani padti hai, fir fetch call karte hain
        transcript_manager = YouTubeTranscriptApi()
        transcript_list = transcript_manager.fetch(video_id, languages=['en', 'hi'])
        
        full_text = " ".join([item['text'] for item in transcript_list])
        clean_text = full_text.replace('\n', ' ')
        
        return jsonify({"transcript": clean_text})

    except AttributeError:
        # Fallback: Agar kismat se purana version install hua ho
        try:
             transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
             full_text = " ".join([item['text'] for item in transcript_list])
             clean_text = full_text.replace('\n', ' ')
             return jsonify({"transcript": clean_text})
        except:
             return jsonify({"error": "Library Version Mismatch. Contact Admin."}), 500

    except TranscriptsDisabled:
        return jsonify({"error": "Subtitles are disabled for this video."}), 404
    except NoTranscriptFound:
        return jsonify({"error": "No transcript found in English/Hindi."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
