# Quick Start: AI Features Setup

## Prerequisites

- Python 3.7+
- Groq API key

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Groq API Key

1. Visit https://console.groq.com/keys
2. Sign up/login
3. Create a new API key
4. Copy the key

### 3. Configure Environment

```bash
# Create .env file
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac

# Edit .env and add:
GROQ_API_KEY=gsk_your_actual_api_key_here
SECRET_KEY=your_random_secret_key_here
```

### 4. Initialize Database

```bash
python init_db.py
```

### 5. Run Application

```bash
python app.py
```

Visit http://localhost:5000

## Test AI Features

1. **Sign up** and create an account
2. **Post a chirp** - Content moderation will check it automatically
3. **Click "AI Features"** button while composing to:
   - Get hashtag suggestions
   - Enhance your content
4. **Click brain icon** (🧠) on any chirp for reply suggestions
5. **View a chirp** and click refresh in sentiment analysis box
6. **Load trending topics** on the timeline
7. **Open a conversation** and click "AI Summary"

## Troubleshooting

**AI not working?**

- Check `.env` file has correct `GROQ_API_KEY`
- Verify internet connection
- Check terminal for error messages
- Ensure dependencies are installed

**Database errors?**

- Delete `chirpx.db`
- Run `python init_db.py` again

## Next Steps

- Read [AI_FEATURES.md](AI_FEATURES.md) for detailed documentation
- Explore different AI features
- Check Groq console for API usage

Enjoy your AI-powered ChirpX! 🚀
