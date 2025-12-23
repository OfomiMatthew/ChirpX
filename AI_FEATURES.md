# ChirpX AI Features Documentation

## Overview

ChirpX now includes powerful AI features powered by Groq API to enhance user experience, content quality, and platform safety.

## AI Features

### 1. **Content Moderation** 🛡️

- **What it does**: Automatically scans chirps for inappropriate content before posting
- **Checks for**:
  - Hate speech and harassment
  - Violence or graphic content
  - Sexual or adult content
  - Spam and misleading information
  - Personal attacks or threats
- **How it works**: When you post a chirp, it's automatically analyzed. If inappropriate content is detected, the post is blocked with an explanation.

### 2. **Spam Detection** 🚫

- **What it does**: Identifies and blocks spam content
- **Detects**:
  - Excessive links or promotional content
  - Repetitive messages
  - Suspicious URLs
  - Get-rich-quick schemes
  - Phishing attempts
  - Too many hashtags
- **Confidence threshold**: 70% or higher blocks the post

### 3. **Smart Reply Suggestions** 💬

- **What it does**: Generates intelligent reply suggestions for any chirp
- **How to use**: Click the brain icon (🧠) on any chirp to see 3 AI-generated reply suggestions
- **Features**:
  - Suggestions match the tone of the original post
  - Diverse responses (supportive, questions, lighthearted)
  - One-click to use a suggestion
- **Location**: Timeline, Explore, and Chirp Detail pages

### 4. **Sentiment Analysis** 📊

- **What it does**: Analyzes the emotional tone and sentiment of chirps
- **Provides**:
  - Sentiment classification (positive, negative, neutral)
  - Sentiment score (-1 to 1)
  - Primary emotions detected (joy, sadness, anger, fear, surprise, love, etc.)
  - Suggested hashtags based on content
- **How to use**: On chirp detail page, click the "Refresh" button in the AI Sentiment Analysis box
- **Caching**: Results are cached in the database for performance

### 5. **Hashtag Suggestions** #️⃣

- **What it does**: Recommends relevant hashtags for your chirp
- **Features**:
  - Context-aware suggestions
  - Mix of popular and specific tags
  - Up to 5 suggestions per chirp
  - One-click to add to your chirp
- **How to use**:
  1. Enable "AI Features" when composing a chirp
  2. Click "Suggest Hashtags"
  3. Click any suggested tag to add it to your chirp

### 6. **Content Enhancement** ✨

- **What it does**: Improves your chirp to make it more engaging
- **Features**:
  - Grammar and clarity improvements
  - Maintains original tone and message
  - Stays within 280 character limit
  - Provides improvement tips
- **How to use**:
  1. Enable "AI Features" when composing a chirp
  2. Click "Enhance Content"
  3. Review the improved version and tips
  4. Click "Use This Version" to apply

### 7. **Trending Topics Analysis** 🔥

- **What it does**: Analyzes recent chirps to identify trending topics
- **Features**:
  - AI-powered topic extraction
  - Relevance scoring (0-100%)
  - Updates from last 24 hours of chirps
  - Visual display with sizing based on relevance
- **How to use**: Click "Load Trending" in the Trending Topics section on the timeline

### 8. **Conversation Summarization** 📝

- **What it does**: Generates concise summaries of direct message conversations
- **Features**:
  - Analyzes last 20 messages
  - Captures main points
  - 1-2 sentence summary
- **How to use**: In any conversation, click "AI Summary" button in the header

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Groq API Key

1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign up or log in
3. Generate a new API key
4. Copy the key

### 3. Configure Environment Variables

1. Copy `.env.example` to `.env`:

   ```bash
   copy .env.example .env  # Windows
   # or
   cp .env.example .env    # Linux/Mac
   ```

2. Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your-actual-groq-api-key-here
   SECRET_KEY=your-random-secret-key
   ```

### 4. Update Database Schema

Run the database initialization to add AI-related tables:

```bash
python init_db.py
```

### 5. Run the Application

```bash
python app.py
```

## API Endpoints

### Get Reply Suggestions

```
GET /ai/reply-suggestions/<chirp_id>
Returns: {"suggestions": ["reply1", "reply2", "reply3"]}
```

### Enhance Content

```
POST /ai/enhance-content
Body: {"content": "your chirp text"}
Returns: {
  "improved_content": "enhanced version",
  "suggestions": ["tip1", "tip2"]
}
```

### Get Hashtag Suggestions

```
POST /ai/hashtag-suggestions
Body: {"content": "your chirp text"}
Returns: {"hashtags": ["Tag1", "Tag2", "Tag3"]}
```

### Get Sentiment Analysis

```
GET /ai/sentiment/<chirp_id>
Returns: {
  "sentiment": "positive",
  "score": 0.85,
  "emotions": ["joy", "excitement"],
  "hashtags": ["Happy", "GoodVibes"]
}
```

### Get Trending Topics

```
GET /ai/trending-topics
Returns: {
  "topics": [
    {"topic": "AI Technology", "relevance": 0.95},
    {"topic": "Climate Change", "relevance": 0.87}
  ]
}
```

### Summarize Conversation

```
GET /ai/conversation-summary/<username>
Returns: {"summary": "Brief conversation summary"}
```

## Technical Details

### AI Model

- **Provider**: Groq
- **Model**: llama-3.3-70b-versatile
- **Characteristics**: Fast inference, versatile, high quality

### Performance Optimizations

1. **Caching**: Sentiment analysis results are cached in `ai_analysis` table
2. **Non-blocking**: AI operations don't block chirp posting
3. **Error Handling**: Graceful fallbacks if AI service fails
4. **Rate Limiting**: Client-side button loading states prevent spam

### Database Schema

New table: `ai_analysis`

```sql
CREATE TABLE ai_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chirp_id INTEGER NOT NULL,
    sentiment TEXT,
    sentiment_score REAL,
    emotions TEXT,              -- JSON array
    suggested_hashtags TEXT,    -- JSON array
    moderation_flag INTEGER DEFAULT 0,
    moderation_reason TEXT,
    spam_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chirp_id) REFERENCES chirps (id) ON DELETE CASCADE
);
```

## Best Practices

### For Users

1. **Content Moderation**: Write respectful, appropriate content to avoid blocks
2. **Hashtags**: Use suggested hashtags to increase discoverability
3. **Enhancement**: Review AI suggestions before applying them
4. **Replies**: Use reply suggestions as inspiration, personalize them

### For Developers

1. **Error Handling**: Always wrap AI calls in try-catch blocks
2. **Fallbacks**: Provide default behaviors if AI fails
3. **Rate Limits**: Monitor Groq API usage to stay within limits
4. **Caching**: Cache results when possible to reduce API calls
5. **User Feedback**: Show loading states during AI operations

## Troubleshooting

### AI Features Not Working

1. **Check API Key**: Ensure `GROQ_API_KEY` is set in `.env`
2. **Install Dependencies**: Run `pip install -r requirements.txt`
3. **Check Console**: Look for error messages in terminal
4. **Network Issues**: Ensure internet connection for API calls

### Content Moderation False Positives

- AI moderation may occasionally flag appropriate content
- Context-dependent decisions may not always be perfect
- Consider implementing a review/appeal system for production

### Performance Issues

1. **Cache Results**: Most AI analyses are cached after first run
2. **Limit Requests**: Avoid rapid-fire AI requests
3. **Background Processing**: Consider moving AI to background jobs for production

## Future Enhancements

Potential additions:

1. **Image Analysis**: Analyze uploaded images for content moderation
2. **Auto-Translation**: Translate chirps to different languages
3. **Smart Notifications**: AI-powered notification prioritization
4. **Content Recommendations**: Personalized chirp recommendations
5. **Writing Assistant**: Real-time writing suggestions as you type
6. **Fact Checking**: Verify claims in chirps
7. **Tone Adjustment**: Adjust chirp tone (formal, casual, professional)

## Cost Considerations

- Groq offers generous free tier
- Monitor usage at [Groq Console](https://console.groq.com)
- Consider caching strategies to minimize API calls
- Implement rate limiting for production use

## Privacy & Safety

- AI analyses are stored locally in your database
- No data is shared with third parties beyond Groq API
- Content moderation helps maintain a safe community
- Users are notified when content is blocked

## Support

For issues or questions:

1. Check error messages in browser console (F12)
2. Review terminal logs for API errors
3. Verify environment variables are set correctly
4. Consult Groq documentation: https://console.groq.com/docs

---

**Note**: AI features require an active internet connection and valid Groq API key. Some features may have usage limits based on your Groq account tier.
