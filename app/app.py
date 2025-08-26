import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from io import BytesIO
from flask import send_file
from dotenv import load_dotenv
from .ai_modeling import generate

# Construct the path to the .env file located in the parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

from whitenoise import WhiteNoise

app = Flask(__name__)
app.wsgi_app = WhiteNoise(app.wsgi_app, root="app/static/")
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')
app.config['BACKGROUND_FOLDER'] = 'background'
app.config['CHARACTER_FOLDER'] = 'character'
app.config['GENERATED_FOLDER'] = 'generated'

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client.sticker

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_json):
        self.user_json = user_json
        self.id = user_json['username']

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    user_json = db.users.find_one({'username': user_id})
    if user_json:
        return User(user_json)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_json = db.users.find_one({'username': username, 'password': password})
        if user_json:
            user = User(user_json)
            login_user(user)
            session.permanent = False
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    user_id = db.users.find_one({'username': current_user.id})['_id']
    backgrounds = db.images.find({'user_id': user_id, 'type': 'background'})
    return render_template('index.html', backgrounds=[bg['filename'] for bg in backgrounds])

@app.route('/characters')
@login_required
def characters():
    user_id = db.users.find_one({'username': current_user.id})['_id']
    characters = db.images.find({'user_id': user_id, 'type': 'character'})
    return render_template('characters.html', characters=[char['filename'] for char in characters], background=request.args.get('background'))

@app.route('/generate', methods=['POST'])
@login_required
def generate_image():
    background_filename = request.form.get('background')
    character_filename = request.form.get('character')

    if not background_filename or not character_filename:
        return redirect(url_for('home'))

    return render_template('generating.html', background=background_filename, character=character_filename)

@app.route('/process_image')
@login_required
def process_image():
    background_filename = request.args.get('background')
    character_filename = request.args.get('character')

    user_id = db.users.find_one({'username': current_user.id})['_id']
    
    background_doc = db.images.find_one({'user_id': user_id, 'filename': background_filename, 'type': 'background'})
    character_doc = db.images.find_one({'user_id': user_id, 'filename': character_filename, 'type': 'character'})

    background_data = background_doc['data']
    character_data = character_doc['data']

    generated_image_data = generate(background_data, character_data)
    
    generated_image_doc = db.generated.insert_one({
        'user_id': user_id,
        'content_type': 'image/png',
        'data': generated_image_data
    })
    
    return redirect(url_for('main_page', generated_image_id=str(generated_image_doc.inserted_id)))

@app.route('/main')
@login_required
def main_page():
    generated_image_id = request.args.get('generated_image_id')
    user = db.users.find_one({'username': current_user.id})
    default_text = user.get('default_text', 'HƏDİYYƏ SƏBƏTİ')
    return render_template('main.html', generated_image_id=generated_image_id, default_text=default_text)

@app.route('/generated/<image_id>')
def generated_image(image_id):
    image_doc = db.generated.find_one({'_id': ObjectId(image_id)})
    return send_file(BytesIO(image_doc['data']), mimetype=image_doc['content_type'])

@app.route('/background/<filename>')
def background_image(filename):
    user_id = db.users.find_one({'username': current_user.id})['_id']
    image_doc = db.images.find_one({'user_id': user_id, 'filename': filename, 'type': 'background'})
    return send_file(BytesIO(image_doc['data']), mimetype=image_doc['content_type'])

@app.route('/character/<filename>')
def character_image(filename):
    user_id = db.users.find_one({'username': current_user.id})['_id']
    image_doc = db.images.find_one({'user_id': user_id, 'filename': filename, 'type': 'character'})
    return send_file(BytesIO(image_doc['data']), mimetype=image_doc['content_type'])
