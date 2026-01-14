const express = require('express');
const cors = require('cors');
const { YoutubeTranscript } = require('youtube-transcript');

const app = express();

// Middleware
app.use(cors()); // Phone ko connect karne ke liye zaroori hai
app.use(express.json());

// 1. Home Route (Test karne ke liye)
app.get('/', (req, res) => {
    res.send('<h1>Node.js Transcriber Server is Running! 🚀</h1>');
});

// 2. Transcribe Route
app.post('/transcribe', async (req, res) => {
    try {
        const { url } = req.body;

        if (!url) {
            return res.status(400).json({ error: "URL nahi bheja bhai!" });
        }

        console.log(`Request aayi hai: ${url}`);

        // Library call
        // config pass kar rahe hain taaki agar English na ho to error na de (generic fetch)
        const transcriptItems = await YoutubeTranscript.fetchTranscript(url);

        if (!transcriptItems || transcriptItems.length === 0) {
            return res.status(404).json({ error: "Transcript nahi mila." });
        }

        // Saare text parts ko jod kar ek paragraph banana
        const fullText = transcriptItems.map(item => item.text).join(' ');

        // Safai (Decode HTML entities like &amp; -> &)
        const cleanText = fullText
            .replace(/&amp;/g, '&')
            .replace(/&quot;/g, '"')
            .replace(/&#39;/g, "'")
            .replace(/\n/g, ' ');

        console.log("Transcript bheja gaya ✅");
        res.json({ transcript: cleanText });

    } catch (error) {
        console.error("Error aaya:", error.message);
        
        // Agar subtitles disabled hain ya video private hai
        if (error.message.includes("Could not retrieve a transcript")) {
             return res.status(404).json({ error: "Is video ke captions/subtitles band hain." });
        }
        
        res.status(500).json({ error: "Server Error: Transcript fetch nahi hua." });
    }
});

// Server Start
const PORT = 5000;
// '0.0.0.0' bahut zaroori hai taaki phone connect ho sake
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server chal gaya: http://0.0.0.0:${PORT}`);
});
