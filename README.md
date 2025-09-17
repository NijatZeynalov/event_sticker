## Event Sticker Generator – Documentation

This repository contains a Flask web app that lets users log in, pick a background and a character image from their library, choose a subject and a visual style, and generate a composited image using Google Gemini image generation.

### Tech Stack
- **Backend**: Flask, Flask-Login
- **Storage**: MongoDB (Atlas or local)
- **AI**: Google Gemini (via `google-genai` or fallback to `google-generativeai`)
- **Static serving**: WhiteNoise

### Project Structure
```
app/
  __init__.py          # Flask app, routes, Mongo, auth
  ai_modeling.py       # Image generation via Google Gemini
  app.py               # WSGI entry re-export
  static/              # Static assets (served via WhiteNoise)
  templates/           # Jinja2 templates (UI screens)
requirements.txt
```

### Prerequisites
- Python 3.10+
- A MongoDB instance (Atlas recommended)
- A Google API key with access to Gemini image generation

### Quickstart (Windows PowerShell)
```powershell
# 1) Clone and enter the folder
git clone <this-repo-url>
cd event

# 2) Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Create a .env file in the repo root
@"
SECRET_KEY=change-this-in-production
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>/<db>?retryWrites=true&w=majority
GOOGLE_API_KEY=your-google-api-key
"@ | Out-File -Encoding utf8 .env

# 5) Run the server
python app\__init__.py
# App runs on http://127.0.0.1:8000/
```

### Environment Variables
Create a `.env` in the repository root (same folder as `requirements.txt`). The app loads it from `app/__init__.py` via `dotenv`.
- **SECRET_KEY**: Flask session secret.
- **MONGO_URI**: Mongo connection string. Example (Atlas):
  `mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority`
- **GOOGLE_API_KEY**: Google API key with access to Gemini image generation.

Important: The current code contains hardcoded credentials in `app/__init__.py` (Mongo) and `app/ai_modeling.py` (Google API key). For security, move these to the `.env` variables above and remove hardcoded values before deploying.

### Data Model (MongoDB)
Database name: `sticker`
- **users**: `{ username: string, password: string, default_text?: string }`
- **images**: `{ user_id: ObjectId, type: 'background'|'character', filename: string, content_type: 'image/png', data: Binary }`
- **generated**: `{ user_id: ObjectId, content_type: 'image/png', data: Binary }`

Minimal seed example (Mongo shell or MongoDB Compass):
```javascript
db.users.insertOne({ username: 'demo', password: 'demo', default_text: 'HƏDİYYƏ SƏBƏTİ' })
// Insert images for the user into `images` with type 'background' or 'character'
```

### Application Flow
1) User logs in at `/login` using a username/password found in `users`.
2) Home (`/`) lists user backgrounds from `images` (type `background`).
3) `/characters` lists character images.
4) `/subject` lets user pick a subject.
5) `/style` lets user pick a rendering style.
6) `/generate` shows a generating screen, then `/process_image` calls Gemini and stores the result in `generated`.
7) `/main` displays the generated image, with optional `default_text` from the user profile.

### Routes
- `GET /login`, `POST /login`: Username/password login (Flask-Login)
- `GET /logout`: Logout
- `GET /` (login required): Background picker
- `GET /characters` (login required): Character picker
- `GET /subject` (login required): Subject chooser
- `GET /style` (login required): Style chooser
- `POST /generate` (login required): Transition to generating page
- `GET /process_image` (login required): Runs generation and redirects to `/main`
- `GET /main` (login required): Shows the generated image
- `GET /generated/<image_id>`: Serves generated image by id
- `GET /background/<filename>`: Serves background image by filename (current user)
- `GET /character/<filename>`: Serves character image by filename (current user)

### Supported Styles
Configured in `app/ai_modeling.py`:
- ghibli
- Muppet Realistic Style
- Pixar 3D
- disney classic
- Lego Style

### Notes on AI Generation
- Uses model: `gemini-2.0-flash-preview-image-generation` via `google-genai` client.
- The code supports both `google-genai` and fallback to `google-generativeai` imports.
- Both images are sent as inline binary parts; the first is treated as background, the second as character.

### Running Behind a WSGI Server
For production, run with Gunicorn (on Linux) and serve via a reverse proxy:
```bash
gunicorn -w 2 -b 0.0.0.0:8000 app:application
```
WhiteNoise is configured to serve `app/static/` directly.

### Security Checklist (Before Deploying)
- Remove hardcoded secrets from source files; use `.env`.
- Use strong `SECRET_KEY` and rotate keys regularly.
- Enforce TLS/HTTPS for any public endpoint.
- Hash and salt user passwords instead of storing plaintext.
- Validate file inputs and MIME types if you later add upload features.

### Troubleshooting
- "Cannot connect to MongoDB": verify `MONGO_URI`, IP allowlist for Atlas, and that `sticker` DB/collections exist.
- "Model not found" or permission errors: ensure `GOOGLE_API_KEY` is valid and has access to the specified Gemini model.
- Empty background/character lists: make sure `images` collection has records for the logged-in user with correct `type` and `filename`.
- 401/redirect loop: ensure you logged in successfully and the session cookie is being set (check `SECRET_KEY`).


