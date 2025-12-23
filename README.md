# ChirpX - AI-Powered Microblogging Platform

A modern microblogging platform built with Flask, SQLite, and Bulma CSS, enhanced with AI features powered by Groq.

## ✨ Features

### Core Social Features

- **User Authentication**: Secure signup, login, and logout
- **Post Chirps**: Share thoughts with a 280-character limit
- **Social Interactions**:
  - Follow/Unfollow users
  - Like chirps
  - Comment on chirps
  - Retweet chirps
  - View personalized timeline
  - Explore all chirps
- **User Profiles**:
  - View user information and their chirps
  - Upload profile pictures
  - Edit profile information (bio, location, website)
- **Direct Messages**: Private conversations with other users
- **Search**: Find users and chirps
- **Responsive Design**: Beautiful UI built with Bulma CSS

### 🤖 AI Features (Powered by Groq)

- **Content Moderation**: Automatic detection of inappropriate content
- **Spam Detection**: Intelligent spam filtering
- **Smart Reply Suggestions**: AI-generated reply recommendations
- **Sentiment Analysis**: Analyze emotions and tone of chirps
- **Hashtag Suggestions**: Get relevant hashtag recommendations
- **Content Enhancement**: Improve your chirps with AI assistance
- **Trending Topics**: AI-powered trending topic analysis
- **Conversation Summarization**: Summarize direct message conversations

[📖 View Complete AI Features Documentation](AI_FEATURES.md)

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Groq API key ([Get one here](https://console.groq.com/keys))

### Installation

1. **Clone the repository** (or download):

   ```bash
   cd ChirpX
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:

   ```bash
   # Copy the example file
   copy .env.example .env  # Windows
   # or
   cp .env.example .env    # Linux/Mac

   # Edit .env and add your keys:
   # GROQ_API_KEY=your_groq_api_key_here
   # SECRET_KEY=your_random_secret_key
   ```

4. **Initialize the database**:

   ```bash
   python init_db.py
   ```

5. **Run the application**:

   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your browser and go to `http://127.0.0.1:5000`

[📘 Detailed Setup Guide](AI_SETUP_GUIDE.md)

## 📁 Project Structure

```
ChirpX/
├── app.py                    # Main Flask application with AI endpoints
├── ai_service.py             # AI service module (Groq integration)
├── schema.sql                # Database schema (includes AI tables)
├── init_db.py                # Database initialization script
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore file
├── AI_FEATURES.md            # Detailed AI features documentation
├── AI_SETUP_GUIDE.md         # Quick setup guide for AI features
├── static/
│   └── uploads/              # User uploaded profile pictures
├── templates/                # HTML templates with AI UI
│   ├── base.html             # Base template with navigation
│   ├── login.html            # Login page
│   ├── signup.html           # Signup page
│   ├── timeline.html         # Home timeline (with AI features)
│   ├── explore.html          # Explore page
│   ├── profile.html          # User profile page
│   ├── search.html           # Search results page
│   ├── chirp_detail.html     # Individual chirp (with sentiment analysis)
│   ├── edit_profile.html     # Edit profile page
│   ├── messages.html         # Direct messages list
│   └── conversation.html     # Conversation view (with AI summary)
└── chirpx.db                 # SQLite database (created after init)
```

## 📊 Database Schema

### Users Table

- id, username, email, password, full_name, bio, location, website, profile_picture, created_at

### Chirps Table

- id, user_id, content, created_at

### Follows Table

- id, follower_id, following_id, created_at

### Likes Table

- id, user_id, chirp_id, created_at

### Comments Table

- id, user_id, chirp_id, content, created_at

### Retweets Table

- id, user_id, chirp_id, created_at

### Messages Table

- id, sender_id, receiver_id, content, read, created_at

### AI Analysis Table (New!)

- id, chirp_id, sentiment, sentiment_score, emotions, suggested_hashtags, moderation_flag, moderation_reason, spam_score, created_at

## 🎯 Usage

### Basic Usage

1. **Create an account** on the signup page
2. **Post chirps** from your timeline
3. **Explore** to find new users and content
4. **Follow users** to see their chirps in your timeline
5. **Like chirps** to show appreciation
6. **Comment on chirps** to join conversations
7. **Retweet chirps** to share with your followers
8. **Upload profile picture** and customize your profile
9. **Search** for specific users or content
10. **Send direct messages** to other users

### AI Features Usage

1. **Enable AI Features** when composing a chirp
2. **Get hashtag suggestions** for your posts
3. **Enhance content** with AI assistance
4. **View sentiment analysis** on any chirp
5. **Get reply suggestions** by clicking the brain icon
6. **Check trending topics** on your timeline
7. **Summarize conversations** in direct messages

## 🔧 API Endpoints

### AI Endpoints

- `GET /ai/reply-suggestions/<chirp_id>` - Get smart reply suggestions
- `POST /ai/enhance-content` - Enhance chirp content
- `POST /ai/hashtag-suggestions` - Get hashtag recommendations
- `GET /ai/sentiment/<chirp_id>` - Analyze chirp sentiment
- `GET /ai/trending-topics` - Get trending topics
- `GET /ai/conversation-summary/<username>` - Summarize conversation

See [AI_FEATURES.md](AI_FEATURES.md) for detailed API documentation.

## 🔐 Security Note

**Important**:

- Change the `SECRET_KEY` in `.env` before deploying to production!
- Never commit your `.env` file to version control
- Keep your Groq API key secure
- Use environment variables for all sensitive data

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: Bulma CSS, Font Awesome
- **Authentication**: Werkzeug password hashing
- **AI**: Groq API (llama-3.3-70b-versatile model)
- **Environment**: python-dotenv

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 License

MIT License - Feel free to use this project for learning and development!

## 🌟 Acknowledgments

- Built with Flask and Bulma CSS
- AI powered by Groq
- Icons by Font Awesome

## 📞 Support

For issues or questions:

1. Check [AI_FEATURES.md](AI_FEATURES.md) for detailed documentation
2. Review [AI_SETUP_GUIDE.md](AI_SETUP_GUIDE.md) for setup help
3. Check console/terminal for error messages

---

**Enjoy your AI-powered social media experience!** 🚀🤖
