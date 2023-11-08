import os
from flask import Flask, flash, request, redirect, url_for,jsonify
from werkzeug.utils import secure_filename
from utility import Meeting_Master,Agile_Master,Retro_Master,Master_AI
from format import *
import json

# UPLOAD_FOLDER = 'meetings'
ALLOWED_EXTENSIONS = {'txt','vtt','docx'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'meetings/1'
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'

global meeting_counter
meeting_counter = 1


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def make_folder(ID):
    # Get the current working directory
    current_directory = os.getcwd()

    # Specify the name of the new folder you want to create
    new_folder_name = "meetings/" + str(ID)

    # Combine the current directory and the new folder name to create the full path
    new_folder_path = os.path.join(current_directory, new_folder_name)

    # Check if the folder already exists
    if not os.path.exists(new_folder_path):
        # Create the new folder
        os.mkdir(new_folder_path)
        # print(f"Folder '{new_folder_name}' created in the current directory.")
    else:
        pass
        # print(f"Folder '{new_folder_name}' already exists in the current directory.")

    return





# @app.route('/meetingminute/<filename>', methods=['GET'])
# def get_meeting_minute(filename):
    
#     if(request.method == 'GET'): 

#         file_name = "processed/"+str(filename)+".json"

#         with open(file_name,'r') as file:
#             data = file.read()
  
        
#         return jsonify({'data': data}) 
#         # return "Got em"

# @app.route('/files/<filename>', methods=['GET'])
# def get_file(filename):
    
#     if(request.method == 'GET'): 

#         file_name = "processed/"+str(filename)+".json"

#         try:

#             with open(file_name,'r') as file:
#                 data = file.read()
  
#             return jsonify({'data': data}) 
#         except:
#             return jsonify({'data': "File not found"})
#         # return "Got em"

@app.route('/files/<id>', methods=['GET'])
def get_file(id):
    
    if(request.method == 'GET'): 

        file_name = "meetings/"+str(id)+"/master_output.json"

        try:

            with open(file_name,'r') as file:
                data = file.read()
  
            return jsonify({'data': data}) 
        except:
            return jsonify({'data': "File not found"})
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

@app.route('/uploadtranscript', methods=[ 'POST'])
def upload_file():
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
            global meeting_counter
            old_meeting_counter = meeting_counter
            make_folder(meeting_counter)
            app.config['UPLOAD_FOLDER'] = 'meetings/' +str(meeting_counter)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("running")
            
            # Access form data
            meta_type = request.form.get('meetingType')
            meta_name = request.form.get('name')

            # meta_name = request.form.get('name')
            # meta_date = request.form.get('date')

            meta_dict = Master_AI(filename,meeting_counter,meta_name,meta_type)

            # make_file_metadata('meetings/' +str(meeting_counter),{'ID':meeting_counter,'title':meta_name,'type':meta_type,'date':'1/1/2020','duration':10,'attendees':["Attendees"]})

            # print(meta_data)
            
            
            meeting_counter = meeting_counter + 1
            
            # print('here 3')

  
            return jsonify({'ID': old_meeting_counter,'title':meta_dict['title'],'type':meta_dict['type'],'date':meta_dict['date'],'attendees':meta_dict['attendees']}) 
    return

@app.route('/masterlist', methods=['GET'])
def return_master_file():
    
    if(request.method == 'GET'): 

        file_name = "master.json"

        try:

            with open(file_name,'r') as file:
                data = file.read()
  
            return jsonify({'data': data}) 
        except:
            return jsonify({'data': "File not found"})
        # return "Got em"

@app.route('/meetinghelp', methods=[ 'POST'])
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