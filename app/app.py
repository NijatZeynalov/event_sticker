import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from .ai_modeling import generate

app = Flask(__name__, static_folder='../static')
app.config['BACKGROUND_FOLDER'] = 'background'
app.config['CHARACTER_FOLDER'] = 'character'
app.config['GENERATED_FOLDER'] = 'generated'

@app.route('/')
def home():
    backgrounds = os.listdir(app.config['BACKGROUND_FOLDER'])
    return render_template('index.html', backgrounds=backgrounds)

@app.route('/characters')
def characters():
    characters = os.listdir(app.config['CHARACTER_FOLDER'])
    return render_template('characters.html', characters=characters, background=request.args.get('background'))

@app.route('/generate', methods=['POST'])
def generate_image():
    background_filename = request.form.get('background')
    character_filename = request.form.get('character')

    if not background_filename or not character_filename:
        return redirect(url_for('home'))

    background_path = os.path.join(app.config['BACKGROUND_FOLDER'], background_filename)
    character_path = os.path.join(app.config['CHARACTER_FOLDER'], character_filename)

    generated_image_filename = generate(background_path, character_path)

    return render_template('main.html', generated_image=generated_image_filename)

@app.route('/generated/<filename>')
def generated_image(filename):
    return send_from_directory(os.path.join('..', app.config['GENERATED_FOLDER']), filename)

@app.route('/background/<filename>')
def background_image(filename):
    return send_from_directory(os.path.join('..', app.config['BACKGROUND_FOLDER']), filename)

@app.route('/character/<filename>')
def character_image(filename):
    return send_from_directory(os.path.join('..', app.config['CHARACTER_FOLDER']), filename)

if __name__ == '__main__':
    os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)
    app.run(debug=True)
