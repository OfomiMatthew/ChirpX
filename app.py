from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from functools import wraps
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Import AI service
from ai_service import get_ai_service

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}
MAX_MEDIA_FILES = 4  # Maximum media files per chirp
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_media_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        return 'image'
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        return 'video'
    return None

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('chirpx.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# Initialize database on startup if it doesn't exist
def ensure_database_exists():
    """Ensure database is initialized on first run"""
    import os
    if not os.path.exists('chirpx.db'):
        print("Database not found. Initializing...")
        init_db()
        print("Database initialized successfully!")
    else:
        # Check if tables exist
        try:
            conn = get_db_connection()
            conn.execute('SELECT 1 FROM users LIMIT 1')
            conn.close()
        except sqlite3.OperationalError:
            # Tables don't exist, initialize
            print("Database exists but tables not found. Initializing...")
            init_db()
            print("Database initialized successfully!")

# Ensure database exists when app starts
ensure_database_exists()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('timeline'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form.get('full_name', '')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('signup'))
        
        conn = get_db_connection()
        
        # Check if user exists
        existing_user = conn.execute('SELECT id FROM users WHERE username = ? OR email = ?',
                                    (username, email)).fetchone()
        if existing_user:
            flash('Username or email already exists!', 'danger')
            conn.close()
            return redirect(url_for('signup'))
        
        # Create user
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)',
                    (username, email, hashed_password, full_name))
        conn.commit()
        conn.close()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Welcome back!', 'success')
            return redirect(url_for('timeline'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/timeline')
@login_required
def timeline():
    conn = get_db_connection()
    
    # Get chirps from followed users and self
    chirps = conn.execute('''
        SELECT c.*, u.username, u.full_name, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id) as like_count,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id AND user_id = ?) as user_liked,
               (SELECT COUNT(*) FROM comments WHERE chirp_id = c.id) as comment_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id) as retweet_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id AND user_id = ?) as user_retweeted,
               (SELECT COUNT(*) FROM bookmarks WHERE chirp_id = c.id AND user_id = ?) as is_bookmarked
        FROM chirps c
        JOIN users u ON c.user_id = u.id
        WHERE c.user_id IN (
            SELECT following_id FROM follows WHERE follower_id = ?
            UNION
            SELECT ?
        )
        ORDER BY c.created_at DESC
    ''', (session['user_id'], session['user_id'], session['user_id'], session['user_id'], session['user_id'])).fetchall()
    
    # Fetch media for each chirp
    chirps_with_media = []
    for chirp in chirps:
        chirp_dict = dict(chirp)
        media = conn.execute('SELECT * FROM chirp_media WHERE chirp_id = ? ORDER BY display_order', (chirp['id'],)).fetchall()
        chirp_dict['media'] = [dict(m) for m in media]
        chirps_with_media.append(chirp_dict)
    
    conn.close()
    return render_template('timeline.html', chirps=chirps_with_media)

@app.route('/explore')
@login_required
def explore():
    conn = get_db_connection()
    
    # Get all chirps
    chirps = conn.execute('''
        SELECT c.*, u.username, u.full_name, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id) as like_count,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id AND user_id = ?) as user_liked,
               (SELECT COUNT(*) FROM comments WHERE chirp_id = c.id) as comment_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id) as retweet_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id AND user_id = ?) as user_retweeted
        FROM chirps c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.created_at DESC
    ''', (session['user_id'], session['user_id'])).fetchall()
    
    conn.close()
    return render_template('explore.html', chirps=chirps)

@app.route('/post_chirp', methods=['POST'])
@login_required
def post_chirp():
    content = request.form['content']
    
    if not content or len(content) > 280:
        flash('Chirp must be between 1 and 280 characters!', 'danger')
        return redirect(url_for('timeline'))
    
    # Handle multiple media uploads
    media_files = []
    if 'media' in request.files:
        files = request.files.getlist('media')
        
        # Limit to MAX_MEDIA_FILES
        if len(files) > MAX_MEDIA_FILES:
            flash(f'You can only upload up to {MAX_MEDIA_FILES} media files per chirp!', 'warning')
            files = files[:MAX_MEDIA_FILES]
        
        for idx, file in enumerate(files):
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                import time
                filename = f"{int(time.time())}_{idx}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                media_url = f"uploads/{filename}"
                media_type = get_media_type(file.filename)
                media_files.append({'url': media_url, 'type': media_type, 'order': idx})
    
    # AI Content Moderation
    try:
        ai = get_ai_service()
        moderation_result = ai.moderate_content(content)
        
        if not moderation_result.get('is_safe', True):
            flash(f"Content moderation: {moderation_result.get('reason', 'Inappropriate content detected')}", 'danger')
            return redirect(url_for('timeline'))
        
        # Spam Detection
        spam_result = ai.detect_spam(content)
        if spam_result.get('is_spam', False) and spam_result.get('confidence', 0) > 0.7:
            flash(f"Spam detected: {spam_result.get('reason', 'Suspicious content')}", 'danger')
            return redirect(url_for('timeline'))
    except Exception as e:
        print(f"AI moderation error: {str(e)}")
        # Continue posting if AI fails
    
    conn = get_db_connection()
    cursor = conn.execute('INSERT INTO chirps (user_id, content) VALUES (?, ?)',
                (session['user_id'], content))
    chirp_id = cursor.lastrowid
    
    # Insert media files
    for media in media_files:
        conn.execute('INSERT INTO chirp_media (chirp_id, media_url, media_type, display_order) VALUES (?, ?, ?, ?)',
                    (chirp_id, media['url'], media['type'], media['order']))
    
    # Analyze sentiment and store in background (non-blocking)
    try:
        ai = get_ai_service()
        sentiment_result = ai.analyze_sentiment(content)
        hashtag_suggestions = ai.suggest_hashtags(content)
        
        conn.execute('''
            INSERT INTO ai_analysis (chirp_id, sentiment, sentiment_score, emotions, suggested_hashtags)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            chirp_id,
            sentiment_result.get('sentiment', 'neutral'),
            sentiment_result.get('score', 0.0),
            json.dumps(sentiment_result.get('emotions', [])),
            json.dumps(hashtag_suggestions)
        ))
    except Exception as e:
        print(f"AI analysis error: {str(e)}")
    
    conn.commit()
    conn.close()
    
    flash('Chirp posted!', 'success')
    return redirect(url_for('timeline'))

@app.route('/like/<int:chirp_id>', methods=['POST'])
@login_required
def like_chirp(chirp_id):
    conn = get_db_connection()
    
    # Check if already liked
    existing_like = conn.execute('SELECT id FROM likes WHERE user_id = ? AND chirp_id = ?',
                                (session['user_id'], chirp_id)).fetchone()
    
    if existing_like:
        # Unlike
        conn.execute('DELETE FROM likes WHERE user_id = ? AND chirp_id = ?',
                    (session['user_id'], chirp_id))
    else:
        # Like
        conn.execute('INSERT INTO likes (user_id, chirp_id) VALUES (?, ?)',
                    (session['user_id'], chirp_id))
    
    conn.commit()
    conn.close()
    
    return redirect(request.referrer or url_for('timeline'))

@app.route('/profile/<username>')
@login_required
def profile(username):
    conn = get_db_connection()
    
    # Get user info
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if not user:
        flash('User not found!', 'danger')
        conn.close()
        return redirect(url_for('timeline'))
    
    # Get user's chirps
    chirps = conn.execute('''
        SELECT c.*, u.username, u.full_name, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id) as like_count,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id AND user_id = ?) as user_liked,
               (SELECT COUNT(*) FROM comments WHERE chirp_id = c.id) as comment_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id) as retweet_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id AND user_id = ?) as user_retweeted
        FROM chirps c
        JOIN users u ON c.user_id = u.id
        WHERE c.user_id = ?
        ORDER BY c.created_at DESC
    ''', (session['user_id'], session['user_id'], user['id'])).fetchall()
    
    # Get follower/following counts
    follower_count = conn.execute('SELECT COUNT(*) as count FROM follows WHERE following_id = ?',
                                  (user['id'],)).fetchone()['count']
    following_count = conn.execute('SELECT COUNT(*) as count FROM follows WHERE follower_id = ?',
                                   (user['id'],)).fetchone()['count']
    
    # Check if current user is following this user
    is_following = conn.execute('SELECT id FROM follows WHERE follower_id = ? AND following_id = ?',
                               (session['user_id'], user['id'])).fetchone()
    
    conn.close()
    
    return render_template('profile.html', user=user, chirps=chirps,
                         follower_count=follower_count, following_count=following_count,
                         is_following=bool(is_following))

@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot follow yourself!', 'warning')
        return redirect(request.referrer or url_for('timeline'))
    
    conn = get_db_connection()
    
    # Check if already following
    existing_follow = conn.execute('SELECT id FROM follows WHERE follower_id = ? AND following_id = ?',
                                  (session['user_id'], user_id)).fetchone()
    
    if existing_follow:
        # Unfollow
        conn.execute('DELETE FROM follows WHERE follower_id = ? AND following_id = ?',
                    (session['user_id'], user_id))
        flash('Unfollowed!', 'info')
    else:
        # Follow
        conn.execute('INSERT INTO follows (follower_id, following_id) VALUES (?, ?)',
                    (session['user_id'], user_id))
        flash('Followed!', 'success')
    
    conn.commit()
    conn.close()
    
    return redirect(request.referrer or url_for('timeline'))

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    
    if not query:
        return render_template('search.html', users=[], chirps=[])
    
    conn = get_db_connection()
    
    # Search users
    users = conn.execute('''
        SELECT id, username, full_name, bio, profile_picture,
               (SELECT COUNT(*) FROM follows WHERE following_id = users.id) as follower_count
        FROM users
        WHERE username LIKE ? OR full_name LIKE ?
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    
    # Search chirps
    chirps = conn.execute('''
        SELECT c.*, u.username, u.full_name, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id) as like_count,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id AND user_id = ?) as user_liked,
               (SELECT COUNT(*) FROM comments WHERE chirp_id = c.id) as comment_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id) as retweet_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id AND user_id = ?) as user_retweeted
        FROM chirps c
        JOIN users u ON c.user_id = u.id
        WHERE c.content LIKE ?
        ORDER BY c.created_at DESC
        LIMIT 50
    ''', (session['user_id'], session['user_id'], f'%{query}%')).fetchall()
    
    conn.close()
    
    return render_template('search.html', users=users, chirps=chirps, query=query)

@app.route('/delete_chirp/<int:chirp_id>', methods=['POST'])
@login_required
def delete_chirp(chirp_id):
    conn = get_db_connection()
    
    # Verify ownership
    chirp = conn.execute('SELECT user_id FROM chirps WHERE id = ?', (chirp_id,)).fetchone()
    
    if not chirp or chirp['user_id'] != session['user_id']:
        flash('You can only delete your own chirps!', 'danger')
    else:
        conn.execute('DELETE FROM chirps WHERE id = ?', (chirp_id,))
        conn.commit()
        flash('Chirp deleted!', 'success')
    
    conn.close()
    return redirect(request.referrer or url_for('timeline'))

@app.route('/retweet/<int:chirp_id>', methods=['POST'])
@login_required
def retweet_chirp(chirp_id):
    conn = get_db_connection()
    
    # Check if already retweeted
    existing_retweet = conn.execute('SELECT id FROM retweets WHERE user_id = ? AND chirp_id = ?',
                                   (session['user_id'], chirp_id)).fetchone()
    
    if existing_retweet:
        # Unretweet
        conn.execute('DELETE FROM retweets WHERE user_id = ? AND chirp_id = ?',
                    (session['user_id'], chirp_id))
        flash('Retweet removed!', 'info')
    else:
        # Retweet
        conn.execute('INSERT INTO retweets (user_id, chirp_id) VALUES (?, ?)',
                    (session['user_id'], chirp_id))
        flash('Retweeted!', 'success')
    
    conn.commit()
    conn.close()
    
    return redirect(request.referrer or url_for('timeline'))

@app.route('/chirp/<int:chirp_id>')
@login_required
def view_chirp(chirp_id):
    conn = get_db_connection()
    
    # Get chirp details
    chirp = conn.execute('''
        SELECT c.*, u.username, u.full_name, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id) as like_count,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id AND user_id = ?) as user_liked,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id) as retweet_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id AND user_id = ?) as user_retweeted
        FROM chirps c
        JOIN users u ON c.user_id = u.id
        WHERE c.id = ?
    ''', (session['user_id'], session['user_id'], chirp_id)).fetchone()
    
    if not chirp:
        flash('Chirp not found!', 'danger')
        conn.close()
        return redirect(url_for('timeline'))
    
    # Get comments
    comments = conn.execute('''
        SELECT c.*, u.username, u.full_name, u.profile_picture
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.chirp_id = ?
        ORDER BY c.created_at ASC
    ''', (chirp_id,)).fetchall()
    
    conn.close()
    
    return render_template('chirp_detail.html', chirp=chirp, comments=comments)

@app.route('/comment/<int:chirp_id>', methods=['POST'])
@login_required
def add_comment(chirp_id):
    content = request.form['content']
    
    if not content or len(content) > 280:
        flash('Comment must be between 1 and 280 characters!', 'danger')
        return redirect(url_for('view_chirp', chirp_id=chirp_id))
    
    conn = get_db_connection()
    conn.execute('INSERT INTO comments (user_id, chirp_id, content) VALUES (?, ?, ?)',
                (session['user_id'], chirp_id, content))
    conn.commit()
    conn.close()
    
    flash('Comment added!', 'success')
    return redirect(url_for('view_chirp', chirp_id=chirp_id))

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    conn = get_db_connection()
    
    # Get comment to find chirp_id and verify ownership
    comment = conn.execute('SELECT user_id, chirp_id FROM comments WHERE id = ?', (comment_id,)).fetchone()
    
    if not comment or comment['user_id'] != session['user_id']:
        flash('You can only delete your own comments!', 'danger')
        conn.close()
        return redirect(request.referrer or url_for('timeline'))
    
    chirp_id = comment['chirp_id']
    conn.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()
    
    flash('Comment deleted!', 'success')
    return redirect(url_for('view_chirp', chirp_id=chirp_id))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    conn = get_db_connection()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '')
        bio = request.form.get('bio', '')
        location = request.form.get('location', '')
        website = request.form.get('website', '')
        
        # Handle profile picture upload
        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{session['user_id']}_{file.filename}")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                profile_picture = f'uploads/{filename}'
        
        # Update user profile
        if profile_picture:
            conn.execute('''
                UPDATE users 
                SET full_name = ?, bio = ?, location = ?, website = ?, profile_picture = ?
                WHERE id = ?
            ''', (full_name, bio, location, website, profile_picture, session['user_id']))
        else:
            conn.execute('''
                UPDATE users 
                SET full_name = ?, bio = ?, location = ?, website = ?
                WHERE id = ?
            ''', (full_name, bio, location, website, session['user_id']))
        
        conn.commit()
        conn.close()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile', username=session['username']))
    
    # GET request - show form
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    
    return render_template('edit_profile.html', user=user)

# Direct Messages Routes
@app.route('/messages')
@login_required
def messages():
    conn = get_db_connection()
    
    # Get all unique users the current user has messaged with
    conversations_query = '''
        SELECT DISTINCT
            CASE 
                WHEN m.sender_id = ? THEN m.receiver_id 
                ELSE m.sender_id 
            END as other_user_id
        FROM messages m
        WHERE m.sender_id = ? OR m.receiver_id = ?
    '''
    
    user_ids = conn.execute(conversations_query, 
                           (session['user_id'], session['user_id'], session['user_id'])).fetchall()
    
    conversations = []
    for row in user_ids:
        other_id = row['other_user_id']
        
        # Get user info
        user = conn.execute('SELECT * FROM users WHERE id = ?', (other_id,)).fetchone()
        
        # Get last message
        last_msg = conn.execute('''
            SELECT content, created_at FROM messages 
            WHERE (sender_id = ? AND receiver_id = ?) 
               OR (sender_id = ? AND receiver_id = ?)
            ORDER BY created_at DESC LIMIT 1
        ''', (session['user_id'], other_id, other_id, session['user_id'])).fetchone()
        
        # Get unread count
        unread = conn.execute('''
            SELECT COUNT(*) as count FROM messages 
            WHERE sender_id = ? AND receiver_id = ? AND read = 0
        ''', (other_id, session['user_id'])).fetchone()
        
        conversations.append({
            'username': user['username'],
            'full_name': user['full_name'],
            'profile_picture': user['profile_picture'],
            'last_message': last_msg['content'] if last_msg else '',
            'last_message_time': last_msg['created_at'] if last_msg else '',
            'unread_count': unread['count']
        })
    
    # Sort by last message time
    conversations.sort(key=lambda x: x['last_message_time'], reverse=True)
    
    # Get total unread count
    unread_total = conn.execute('''
        SELECT COUNT(*) as count FROM messages 
        WHERE receiver_id = ? AND read = 0
    ''', (session['user_id'],)).fetchone()['count']
    
    conn.close()
    
    return render_template('messages.html', conversations=conversations, unread_total=unread_total)

@app.route('/messages/<username>')
@login_required
def conversation(username):
    conn = get_db_connection()
    
    # Get the other user
    other_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if not other_user:
        conn.close()
        flash('User not found.', 'danger')
        return redirect(url_for('messages'))
    
    # Mark messages from this user as read
    conn.execute('''
        UPDATE messages SET read = 1 
        WHERE sender_id = ? AND receiver_id = ? AND read = 0
    ''', (other_user['id'], session['user_id']))
    conn.commit()
    
    # Get all messages between these two users
    msgs = conn.execute('''
        SELECT m.*, u.username, u.profile_picture
        FROM messages m
        JOIN users u ON u.id = m.sender_id
        WHERE (m.sender_id = ? AND m.receiver_id = ?) 
           OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.created_at ASC
    ''', (session['user_id'], other_user['id'], other_user['id'], session['user_id'])).fetchall()
    
    conn.close()
    
    return render_template('conversation.html', other_user=other_user, messages=msgs)

@app.route('/messages/send/<username>', methods=['POST'])
@login_required
def send_message(username):
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Message cannot be empty.', 'danger')
        return redirect(url_for('conversation', username=username))
    
    if len(content) > 1000:
        flash('Message is too long. Maximum 1000 characters.', 'danger')
        return redirect(url_for('conversation', username=username))
    
    conn = get_db_connection()
    
    # Get receiver user
    receiver = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    
    if not receiver:
        conn.close()
        flash('User not found.', 'danger')
        return redirect(url_for('messages'))
    
    # Insert message
    conn.execute('''
        INSERT INTO messages (sender_id, receiver_id, content)
        VALUES (?, ?, ?)
    ''', (session['user_id'], receiver['id'], content))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('conversation', username=username))

@app.route('/messages/new/<username>')
@login_required
def new_message(username):
    """Start a new conversation with a user"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('explore'))
    
    return redirect(url_for('conversation', username=username))

# ============== AI Feature Endpoints ==============

@app.route('/ai/reply-suggestions/<int:chirp_id>')
@login_required
def get_reply_suggestions(chirp_id):
    """Get AI-generated reply suggestions for a chirp"""
    conn = get_db_connection()
    chirp = conn.execute('SELECT content FROM chirps WHERE id = ?', (chirp_id,)).fetchone()
    conn.close()
    
    if not chirp:
        return jsonify({'error': 'Chirp not found'}), 404
    
    try:
        ai = get_ai_service()
        suggestions = ai.generate_reply_suggestions(chirp['content'], num_suggestions=3)
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai/enhance-content', methods=['POST'])
@login_required
def enhance_content():
    """Get AI suggestions to improve chirp content"""
    data = request.get_json()
    content = data.get('content', '')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    try:
        ai = get_ai_service()
        result = ai.enhance_content(content)
        return jsonify(result)
    except ValueError as ve:
        print(f"AI Service Error: {str(ve)}")
        return jsonify({'error': f'AI service configuration error: {str(ve)}'}), 500
    except Exception as e:
        print(f"Error in enhance_content: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/ai/hashtag-suggestions', methods=['POST'])
@login_required
def get_hashtag_suggestions():
    """Get AI-generated hashtag suggestions"""
    data = request.get_json()
    content = data.get('content', '')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    try:
        ai = get_ai_service()
        hashtags = ai.suggest_hashtags(content, num_tags=5)
        return jsonify({'hashtags': hashtags})
    except ValueError as ve:
        print(f"AI Service Error: {str(ve)}")
        return jsonify({'error': f'AI service configuration error: {str(ve)}'}), 500
    except Exception as e:
        print(f"Error in hashtag_suggestions: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/ai/sentiment/<int:chirp_id>')
@login_required
def get_chirp_sentiment(chirp_id):
    """Get sentiment analysis for a chirp"""
    conn = get_db_connection()
    
    # Check if analysis exists in cache
    analysis = conn.execute('''
        SELECT sentiment, sentiment_score, emotions, suggested_hashtags
        FROM ai_analysis WHERE chirp_id = ?
    ''', (chirp_id,)).fetchone()
    
    if analysis:
        conn.close()
        return jsonify({
            'sentiment': analysis['sentiment'],
            'score': analysis['sentiment_score'],
            'emotions': json.loads(analysis['emotions']) if analysis['emotions'] else [],
            'hashtags': json.loads(analysis['suggested_hashtags']) if analysis['suggested_hashtags'] else []
        })
    
    # If not cached, analyze now
    chirp = conn.execute('SELECT content FROM chirps WHERE id = ?', (chirp_id,)).fetchone()
    
    if not chirp:
        conn.close()
        return jsonify({'error': 'Chirp not found'}), 404
    
    try:
        ai = get_ai_service()
        result = ai.analyze_sentiment(chirp['content'])
        
        # Cache the result
        conn.execute('''
            INSERT INTO ai_analysis (chirp_id, sentiment, sentiment_score, emotions)
            VALUES (?, ?, ?, ?)
        ''', (chirp_id, result['sentiment'], result['score'], json.dumps(result['emotions'])))
        conn.commit()
        conn.close()
        
        return jsonify(result)
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/ai/trending-topics')
@login_required
def get_trending_topics():
    """Get AI-analyzed trending topics from recent chirps"""
    conn = get_db_connection()
    
    # Get recent chirps (last 24 hours)
    recent_chirps = conn.execute('''
        SELECT content FROM chirps
        WHERE created_at >= datetime('now', '-1 day')
        ORDER BY created_at DESC
        LIMIT 100
    ''').fetchall()
    
    conn.close()
    
    if not recent_chirps:
        return jsonify({'topics': []})
    
    try:
        ai = get_ai_service()
        chirp_texts = [chirp['content'] for chirp in recent_chirps]
        topics = ai.generate_trending_topics(chirp_texts, top_n=5)
        return jsonify({'topics': topics})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai/conversation-summary/<username>')
@login_required
def summarize_conversation(username):
    """Get AI summary of a conversation"""
    conn = get_db_connection()
    
    other_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    
    if not other_user:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    
    # Get last 20 messages
    messages = conn.execute('''
        SELECT m.content, u.username
        FROM messages m
        JOIN users u ON u.id = m.sender_id
        WHERE (m.sender_id = ? AND m.receiver_id = ?) 
           OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.created_at DESC
        LIMIT 20
    ''', (session['user_id'], other_user['id'], other_user['id'], session['user_id'])).fetchall()
    
    conn.close()
    
    if not messages:
        return jsonify({'summary': 'No messages to summarize'})
    
    try:
        ai = get_ai_service()
        message_list = [{'username': msg['username'], 'content': msg['content']} for msg in reversed(messages)]
        summary = ai.summarize_conversation(message_list)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== Bookmark Endpoints ==============

@app.route('/bookmark/<int:chirp_id>', methods=['POST'])
@login_required
def bookmark_chirp(chirp_id):
    """Bookmark or unbookmark a chirp"""
    conn = get_db_connection()
    
    # Check if already bookmarked
    existing_bookmark = conn.execute('SELECT id FROM bookmarks WHERE user_id = ? AND chirp_id = ?',
                                    (session['user_id'], chirp_id)).fetchone()
    
    if existing_bookmark:
        # Remove bookmark
        conn.execute('DELETE FROM bookmarks WHERE user_id = ? AND chirp_id = ?',
                    (session['user_id'], chirp_id))
        flash('Bookmark removed!', 'info')
    else:
        # Add bookmark
        conn.execute('INSERT INTO bookmarks (user_id, chirp_id) VALUES (?, ?)',
                    (session['user_id'], chirp_id))
        flash('Chirp bookmarked!', 'success')
    
    conn.commit()
    conn.close()
    
    return redirect(request.referrer or url_for('timeline'))

@app.route('/bookmarks')
@login_required
def bookmarks():
    """View all bookmarked chirps"""
    conn = get_db_connection()
    
    chirps = conn.execute('''
        SELECT c.*, u.username, u.full_name, u.profile_picture,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id) as like_count,
               (SELECT COUNT(*) FROM likes WHERE chirp_id = c.id AND user_id = ?) as user_liked,
               (SELECT COUNT(*) FROM comments WHERE chirp_id = c.id) as comment_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id) as retweet_count,
               (SELECT COUNT(*) FROM retweets WHERE chirp_id = c.id AND user_id = ?) as user_retweeted,
               1 as user_bookmarked
        FROM chirps c
        JOIN users u ON c.user_id = u.id
        JOIN bookmarks b ON b.chirp_id = c.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    ''', (session['user_id'], session['user_id'], session['user_id'])).fetchall()
    
    conn.close()
    return render_template('bookmarks.html', chirps=chirps)

# ============== Who to Follow ==============

@app.route('/api/who-to-follow')
@login_required
def who_to_follow():
    """Get suggested users to follow"""
    conn = get_db_connection()
    
    # Get users not currently followed, ordered by follower count
    suggestions = conn.execute('''
        SELECT u.id, u.username, u.full_name, u.profile_picture, u.bio,
               (SELECT COUNT(*) FROM follows WHERE following_id = u.id) as follower_count
        FROM users u
        WHERE u.id != ?
        AND u.id NOT IN (SELECT following_id FROM follows WHERE follower_id = ?)
        ORDER BY follower_count DESC
        LIMIT 5
    ''', (session['user_id'], session['user_id'])).fetchall()
    
    conn.close()
    
    return jsonify([dict(user) for user in suggestions])

# ============== AI Image Generation ==============

@app.route('/ai/generate-image', methods=['POST'])
@login_required
def generate_image():
    """Generate image using Pollinations.ai (free) based on description"""
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    
    try:
        ai = get_ai_service()
        result = ai.generate_image_with_pollinations(prompt)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'image_path': result['image_path'],
                'type': result['type'],
                'message': 'Image generated successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate image')
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
