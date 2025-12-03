require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Auth, MemoryStorage } = require('@campnetwork/origin');

const app = express();
app.use(cors());
app.use(express.json());

// Add this right after app.use(express.json());
app.get('/', (req, res) => {
    res.send('Server is running!');
});

// Ensure ORIGIN_CLIENT_ID is provided
if (!process.env.ORIGIN_CLIENT_ID) {
    console.error('❌ ORIGIN_CLIENT_ID is missing in your .env file');
    process.exit(1);
}

// Initialize Auth
const auth = new Auth({
    clientId: process.env.ORIGIN_CLIENT_ID,
    redirectUri: 'http://localhost:8000/callback', // your callback URL
    environment: 'DEVELOPMENT',
    storage: new MemoryStorage()
});

// --- Health Check ---
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok',
        service: 'CampusAI Origin Microservice',
        authenticated: auth ? true : false
    });
});

// --- Get linked socials for authenticated user ---
app.get('/auth/socials', async (req, res) => {
    try {
        const linked = await auth.getLinkedSocials();
        res.json({ success: true, data: linked });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// --- Fetch Twitter user by username ---
app.get('/twitter/user/:username', async (req, res) => {
    try {
        const twitter = await auth.getTwitterClient();
        const user = await twitter.fetchUserByUsername(req.params.username);
        res.json({ success: true, data: user });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// --- Fetch Twitter tweets by username ---
app.get('/twitter/tweets/:username', async (req, res) => {
    try {
        const { page = 1, limit = 10 } = req.query;
        const twitter = await auth.getTwitterClient();
        const tweets = await twitter.fetchTweetsByUsername(
            req.params.username,
            parseInt(page),
            parseInt(limit)
        );
        res.json({ success: true, data: tweets });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// --- Fetch Spotify saved tracks ---
app.get('/spotify/tracks/:spotifyId', async (req, res) => {
    try {
        const spotify = await auth.getSpotifyClient();
        const tracks = await spotify.fetchSavedTracksById(req.params.spotifyId);
        res.json({ success: true, data: tracks });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// --- Fetch TikTok user by username ---
app.get('/tiktok/user/:username', async (req, res) => {
    try {
        const tiktok = await auth.getTikTokClient();
        const user = await tiktok.fetchUserByUsername(req.params.username);
        res.json({ success: true, data: user });
    } catch (err) {
        res.status(500).json({ success: false, error: err.message });
    }
});

// --- Start server ---
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`🚀 CampusAI Origin Microservice running on port ${PORT}`);
    console.log(`✅ Client ID configured`);
    console.log(`📍 Health check: http://localhost:${PORT}/health`);
});
