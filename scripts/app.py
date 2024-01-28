from flask import Flask
from flask import request, render_template, flash
import os

UPLOAD_FOLDER = '../data/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.environ['FLASK_SECRET']


@app.route("/")
def hello_world():
    return render_template('home.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return '''<!DOCTYPE html><html><title>Failure</title> <h1>No file part</h1></html>'''
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return '''<!DOCTYPE html><html><title>Failure</title> <h1>No selected file</h1></html>'''
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return '''<!DOCTYPE html><html><title>Success</title> <h1>File Uploaded</h1></html>'''
    
        return '''<!DOCTYPE html><html><title>Success</title> <h1>File Uploaded</h1></html>'''
