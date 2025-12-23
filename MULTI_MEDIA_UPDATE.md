# Multiple Media Upload & AI Image Generation - Update Documentation

## Overview

ChirpX now supports uploading up to **4 media files** (images/videos) per chirp and generates **ASCII art** using the Groq API.

---

## 🎯 New Features

### 1. Multiple Media Upload

- **Upload up to 4 files** per chirp (images and/or videos)
- Supported formats:
  - **Images**: PNG, JPG, JPEG, GIF, WebP
  - **Videos**: MP4, MOV, AVI, WebM
- Maximum file size: **100MB** total
- Files are displayed in a responsive grid layout

### 2. AI-Powered ASCII Art Generation

- Generate ASCII art using Groq API (llama-3.3-70b-versatile)
- Creative text-based artwork based on your prompts
- Copy generated ASCII art to clipboard
- View in fullscreen modal with dark theme

---

## 📊 Database Changes

### New Table: `chirp_media`

```sql
CREATE TABLE chirp_media (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chirp_id INTEGER NOT NULL,
    media_url TEXT NOT NULL,
    media_type TEXT NOT NULL,
    display_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chirp_id) REFERENCES chirps (id) ON DELETE CASCADE
);

CREATE INDEX idx_chirp_media_chirp_id ON chirp_media(chirp_id);
```

### Migration Notes

- Old `media_url` and `media_type` columns **removed** from `chirps` table
- Media is now stored in separate `chirp_media` table (one-to-many relationship)
- Cascading delete ensures media files are removed when a chirp is deleted
- Database has been reinitialized with the new schema

---

## 🔧 Backend Changes

### File Upload Configuration (`app.py`)

```python
MAX_MEDIA_FILES = 4  # Maximum files per chirp
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max upload
```

### Updated `post_chirp()` Function

- Uses `request.files.getlist('media')` for multiple file handling
- Validates file count (max 4 files)
- Saves files with unique names: `{timestamp}_{index}_{filename}`
- Inserts each file into `chirp_media` table with `display_order`

### Updated `timeline()` Function

- Fetches media separately from `chirp_media` table
- Joins media to chirps as an array: `chirp['media']`
- Each chirp dict now has a `media` list of dictionaries

### AI Image Generation (`ai_service.py`)

```python
def generate_image_with_groq(self, prompt):
    """
    Generates ASCII art using Groq API
    - Temperature: 0.9 (high creativity)
    - Max tokens: 1000
    - Saves to: static/uploads/ascii_art_{timestamp}.txt
    - Returns: {'success': True, 'image_path': str, 'ascii_art': str, 'type': 'ascii'}
    """
```

---

## 🎨 Frontend Changes

### Multiple File Preview (`timeline.html`)

**New JavaScript Functions:**

1. **`previewMedia(input)`**

   - Handles multiple file selections
   - Shows grid preview (2x2 for 4 files)
   - Displays file names and types
   - Limits to 4 files with alert

2. **`removeMedia(index)`**

   - Removes individual files from preview
   - Rebuilds `DataTransfer` object
   - Updates file counter

3. **`updateFileCounter()`**

   - Shows "X/4 files" indicator

4. **`openMediaModal(src, type)`**

   - Fullscreen image/video viewer
   - Click to close
   - Responsive sizing

5. **AI Image Generation Modal**
   - Displays ASCII art in monospace font
   - Copy to clipboard functionality
   - Dark theme background

### HTML Updates

```html
<!-- Multiple file input -->
<input
  type="file"
  id="media-input"
  name="media"
  accept="image/*,video/*"
  multiple
/>
<span id="file-counter" class="text-xs"></span>

<!-- Preview container (grid layout) -->
<div id="media-previews" class="grid grid-cols-2 gap-2"></div>

<!-- Chirp display (loops through media array) -->
{% if chirp['media'] and chirp['media']|length > 0 %}
<div
  class="grid gap-2 {% if chirp['media']|length == 2 %}grid-cols-2{% endif %}"
>
  {% for media in chirp['media'] %} {% if media['media_type'] == 'image' %}
  <img
    src="{{ url_for('static', filename=media['media_url']) }}"
    onclick="openMediaModal('{{ url_for('static', filename=media['media_url']) }}', 'image')"
  />
  {% elif media['media_type'] == 'video' %}
  <video
    controls
    src="{{ url_for('static', filename=media['media_url']) }}"
  ></video>
  {% endif %} {% endfor %}
</div>
{% endif %}
```

---

## 🚀 Usage Guide

### Uploading Multiple Media Files

1. Click the **"Media (Max 4)"** button in the compose box
2. Select up to 4 images/videos
3. Preview shows thumbnails with remove buttons (hover to see)
4. File counter displays: "2/4 files"
5. Click **Chirp** to post

### Generating AI Images (ASCII Art)

1. Click the **"AI Image"** button (sparkles icon)
2. Enter a prompt (e.g., "A cat playing piano")
3. Wait for generation (~3-5 seconds)
4. View ASCII art in modal
5. Copy to clipboard or close

### Viewing Media

- Click on any image to view fullscreen
- Videos play inline with controls
- Multiple media displays in responsive grid:
  - 1 file: Full width
  - 2 files: 2 columns
  - 3 files: 2 columns (first spans 2 cols)
  - 4 files: 2x2 grid

---

## ⚠️ Important Notes

### About Groq Image Generation

- Groq API does **not support actual image generation** (it's a text-based LLM)
- We implemented **ASCII art** as a creative workaround
- ASCII art is saved as `.txt` files in `static/uploads/`
- For real image generation, consider:
  - **DALL-E API** (OpenAI)
  - **Stable Diffusion API** (Stability AI)
  - **Midjourney API**

### File Upload Limits

- Backend validates file count (max 4)
- Frontend alerts if user selects more than 4
- Files exceeding 100MB total will fail upload
- Only first 4 files are processed if more are selected

### Compatibility

- Requires modern browsers (FileReader API, DataTransfer)
- Grid layout requires Tailwind CSS 3.x
- Videos may not play on all browsers (codec support)

---

## 🧪 Testing Checklist

- [x] Database schema updated and initialized
- [x] Backend handles multiple file uploads
- [x] Files save with unique names
- [x] Media displays in grid layout
- [x] Individual file removal works
- [x] File counter updates correctly
- [x] ASCII art generates successfully
- [x] Modal displays ASCII art properly
- [x] Copy to clipboard works
- [x] Fullscreen image viewer works
- [ ] Test with 1, 2, 3, and 4 files
- [ ] Test with videos
- [ ] Test file size limits
- [ ] Test on mobile devices
- [ ] Update other templates (explore, profile, etc.)

---

## 📝 TODO: Update Other Templates

The following templates still need media display updates:

1. **explore.html** - Explore feed chirps
2. **profile.html** - User profile chirps
3. **bookmarks.html** - Bookmarked chirps
4. **search.html** - Search results
5. **chirp_detail.html** - Individual chirp page

**Required changes:**

```django
<!-- Replace old single media -->
{% if chirp['media_url'] %} ... {% endif %}

<!-- With new multi-media loop -->
{% if chirp['media'] and chirp['media']|length > 0 %}
  {% for media in chirp['media'] %}
    ...
  {% endfor %}
{% endif %}
```

---

## 🔗 API Endpoints

### POST `/chirp` (Updated)

- Accepts multiple files via `request.files.getlist('media')`
- Returns 400 if more than 4 files
- Saves each file with unique timestamp and index

### POST `/ai/generate-image` (Updated)

- Generates ASCII art using Groq
- Body: `{"prompt": "your description"}`
- Response:

```json
{
  "success": true,
  "image_path": "uploads/ascii_art_1234567890.txt",
  "ascii_art": "...",
  "type": "ascii"
}
```

---

## 🎉 Summary

✅ **Multiple media upload** fully implemented (up to 4 files)  
✅ **ASCII art generation** using Groq API  
✅ **Responsive grid layouts** for media display  
✅ **Fullscreen modals** for images and ASCII art  
✅ **Database restructured** with separate `chirp_media` table  
✅ **File management** with preview, counter, and removal

**Next Steps:**

- Test thoroughly with different file types and counts
- Update remaining templates (explore, profile, bookmarks, etc.)
- Consider adding real image generation API (DALL-E, Stable Diffusion)
- Add video thumbnails for better preview experience
- Implement lazy loading for media-heavy feeds

---

## 📞 Support

For issues or questions:

- Check browser console for JavaScript errors
- Verify file formats are supported
- Ensure Groq API key is set in environment
- Check `static/uploads/` folder permissions

**Server Running:** http://127.0.0.1:5000  
**Debug Mode:** ON  
**Database:** SQLite (reinitialized)
