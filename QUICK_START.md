# ChirpX - Quick Start Guide

## 🚀 Getting Started

### First Time Setup

```bash
# 1. Navigate to project
cd ChirpX

# 2. Install dependencies (if not already installed)
pip install -r requirements.txt

# 3. Initialize database
python init_db.py

# 4. Run the application
python app.py
```

### Access the Application

Open your browser and go to: **http://127.0.0.1:5000**

---

## 📱 Feature Overview

### 🏠 Home Timeline

**URL:** `/timeline`

- Post new chirps (280 char limit)
- See chirps from people you follow
- Interact with chirps:
  - ❤️ Like/Unlike
  - 💬 Comment (click to view)
  - 🔄 Retweet/Unretweet
  - 🗑️ Delete (your own chirps)

### 🌍 Explore Page

**URL:** `/explore`

- View all chirps from all users
- Discover new content
- Same interaction options as timeline

### 👤 User Profile

**URL:** `/profile/<username>`

- View user's information
- See all their chirps
- Follow/Unfollow button (for other users)
- Edit Profile button (for your own profile)
- Stats: Followers, Following, Join date

### ✏️ Edit Profile

**URL:** `/edit_profile`

- Upload profile picture
- Update full name
- Write bio
- Add location
- Add website URL

### 💬 Chirp Details

**URL:** `/chirp/<chirp_id>`

- View individual chirp
- See all comments
- Add your own comment
- Like/Retweet the chirp
- Delete (if it's your chirp)

### 🔍 Search

**URL:** `/search?q=<query>`

- Search for users by username or name
- Search for chirps by content
- Click on results to view profiles or chirps

---

## 🎯 Key Workflows

### Creating Your First Chirp

1. Log in to your account
2. On the timeline, type in the "What's happening?" box
3. Watch the character counter (max 280)
4. Click "Chirp" to post

### Engaging with Content

1. **Like**: Click the heart icon
2. **Comment**: Click the chirp content or comment icon
3. **Retweet**: Click the retweet icon (turns teal)
4. **Share**: Copy the chirp URL from the detail page

### Building Your Profile

1. Go to your profile
2. Click "Edit Profile"
3. Upload a profile picture (JPG, PNG, or GIF)
4. Fill in your information
5. Click "Save Changes"

### Following Users

1. Search for users or find them in Explore
2. Click on their profile
3. Click "Follow" button
4. Their chirps now appear in your timeline

### Managing Comments

1. Click on any chirp to view details
2. Scroll to comment section
3. Type your comment (max 280 chars)
4. Click "Comment"
5. Delete your comments using the delete button

---

## 🎨 Color Guide

- **Primary (Purple)**: Main actions, buttons
- **Red**: Likes (when active)
- **Teal**: Retweets (when active)
- **Grey**: Neutral actions, metadata
- **White/Light**: Content backgrounds

---

## 🔐 Security Notes

**Important for Production:**

1. Change `app.secret_key` in `app.py`
2. Use HTTPS for file uploads
3. Set up proper user authentication
4. Configure proper file storage (not local disk)
5. Add rate limiting
6. Implement CSRF protection

---

## 🐛 Troubleshooting

### Database Issues

```bash
# Reinitialize database
python init_db.py
```

### Upload Directory Missing

The app creates it automatically, but you can manually create:

```bash
mkdir -p static/uploads
```

### Port Already in Use

Change the port in `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to different port
```

---

## 📊 Database Tables Overview

| Table    | Purpose                    |
| -------- | -------------------------- |
| users    | User accounts and profiles |
| chirps   | All posted chirps          |
| comments | Comments on chirps         |
| likes    | Chirp likes                |
| retweets | Chirp retweets             |
| follows  | User follow relationships  |

---

## 🎓 Learning Resources

Built with:

- **Flask**: Web framework - https://flask.palletsprojects.com/
- **SQLite**: Database - https://www.sqlite.org/
- **Bulma**: CSS framework - https://bulma.io/
- **Font Awesome**: Icons - https://fontawesome.com/

---

## 💡 Tips & Tricks

1. **Use hashtags** in chirps for better discoverability
2. **Engage with others** to build your network
3. **Post regularly** to keep your followers engaged
4. **Upload a profile picture** to make your profile stand out
5. **Write a bio** to tell people about yourself
6. **Follow interesting people** to curate your timeline
7. **Use comments** to have conversations
8. **Retweet** to share content you like

---

## 🌟 What's Next?

Potential features to add:

- Direct messaging
- Notifications
- Hashtag pages
- User mentions (@username)
- Image/video uploads in chirps
- Trending topics
- User verification
- Bookmarks
- Lists

---

Enjoy using ChirpX! 🐦✨
