import os
from flask import Flask, flash, request, redirect, url_for,jsonify
from werkzeug.utils import secure_filename
from utility import Meeting_Master,Agile_Master,Retro_Master
from format import *
import json

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt','vtt','docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/meetingminute', methods=['GET'])
def get_meeting_minute():
    
    if(request.method == 'GET'): 

        with open("processed/minutes.json",'r') as file:
            data = file.read()
  
        
        return jsonify({'data': data}) 
        # return "Got em"



@app.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            print('here 1')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            print('here 2')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            Meeting_Master(filename)
            print('here 3')
            # return redirect(url_for('download_file', name=filename))
            return
            return redirect(request.url)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploadmeeting', methods=[ 'POST'])
def meeting_route():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            print('here 1')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            print('here 2')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            to_return = Meeting_Master(filename)
            print('here 3')

            out_file = open("processed/meeting.json", "w")  
    
            json.dump(to_return, out_file, indent = 6)  
    
            out_file.close()
  
            return jsonify({'data': to_return}) 
    return

@app.route('/agilehelp', methods=[ 'POST'])
def agile_route():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            print('here 1')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            print('here 2')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            to_return = Agile_Master(filename)
            print('here 3')

            out_file = open("processed/agile.json", "w")  
    
            json.dump(to_return, out_file, indent = 6)  
    
            out_file.close()
  
            return jsonify({'data': to_return}) 
    return

@app.route('/retrohelp', methods=[ 'POST'])
def retro_route():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            print('here 1')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            print('here 2')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            to_return = Retro_Master(filename)
            print('here 3')

            out_file = open("processed/retro.json", "w")  
    
            json.dump(to_return, out_file, indent = 6)  
    
            out_file.close()
  
            return jsonify({'data': to_return}) 
    return

if __name__ == '__main__':
    app.run()