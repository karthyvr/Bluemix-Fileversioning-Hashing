# Assignment - 2 - can be accessed from the URL : http://karthytestapp.mybluemix.net/
# Karthy Vaiyampalayam Ramakrishnan
# student id : 1001244142
import os
import json
import hashlib
import couchdb
from flask import Flask, request, redirect, url_for, render_template, send_file, Response, make_response
from datetime import datetime
import werkzeug
import swiftclient.client as swiftclient
import base64
# Reffered to various sources from google,github,couch db documentation sites and flask tutorial and youtube videos

app = Flask(__name__)
# home page for this application
@app.route('/')
@app.route('/index')
def welcome():
    return render_template('index.html')

# below function is used for file saving mechanism
# checks for the same file name and if it matches checks the hashcode and if its different then save the file
# # else do not save the file
@app.route('/goupload')
def goupload():
    print 'in goupload'
    return render_template('upload.html')

# actual upload method
@app.route('/upload', methods=['POST'])
def upload():
    print 'inside upload file '
    input_file = request.files['input_file']
    if file:
        filename = input_file.filename
        content = input_file.read()
    encoded_string = base64.b64encode(content)
    # computing the hash value for the input file
    input_hash_value = hashlib.md5(content).hexdigest()
    print "before time"
    print datetime.now()
    # compute the current time stamp
    currenttime = datetime.now().strftime('%b%d,%Y-%X')
    print currenttime
    db = getconnection()
    # Try to access the file doc to see if it exists.
    # create a record/document if the file does not exist in DB already
    # Note : In DB file name is used for the _id column, to make retrieval easy

    temp_version = 0

    for id in db:
        doc = db[id]
        if doc['filename'] == filename:

            if doc['hash_value'] == input_hash_value:
                print " file already exists ddddddddddddd"
                upload_message = filename +' uploaded File exists already..!'
                    # print upload_message
                return render_template('upload.html', result_msg=upload_message)
            elif temp_version < doc['version']:
                temp_version = doc['version']
                print " within elseifffffffff "


    print"in else loop"
    file_doc_obj = {
            # '_id' : temp_version + 1+':'+filename,
            'filename': filename,
            '_attachments':
                {
                    filename:
                        {
                            # 'content_type': 'text\/plain',
                            'data': encoded_string
                        }
                },
            'hash_value': input_hash_value,
            'version': temp_version + 1,
            'created_dt': currenttime
    }

    doc_id, doc_rev = db.save(file_doc_obj)

    upload_message = filename +' uploaded successfully..!'
    # print upload_message
    return render_template('upload.html', result_msg=upload_message)

# below function is used for listing
# all the documents in the couch db
@app.route('/list')
def list():
    print "inside the list file function "
    files_list = listalldocuments()
    return render_template('list.html', files_list=files_list)

def listalldocuments():
    db = getconnection()
    files_list = []
    for id in db:
        doc = db[id]
        files_list.append(doc)
        print doc['filename']
        print doc['hash_value']
        print doc['version']
    return files_list

# both the delete and download share the common variables file name and version so it can be reused
# from this function we route it to delete or download

@app.route('/deleteordownload')
def deleteordownload():
    print "deleteOrDownload"
    print 'file name ', request.args.get('filename')
    print 'file version ', request.args.get('version')
    print 'operation ', request.args.get('operation')
    ip_filename = request.args.get('filename')
    ip_version =  request.args.get('version')
    ip_operation =  request.args.get('operation')

    if ip_operation == 'Download':
        return redirect(url_for('download', filename=ip_filename, version=ip_version))
    elif ip_operation == 'Delete':
        return redirect(url_for('delete', filename=ip_filename, version=ip_version))

# below function is used to take the filename and fileversion as input then
#  delete the corresponding document in the database
@app.route('/delete/<filename>/<version>')
def delete(filename, version):
    print "In Delete"
    print 'file name ', filename
    print 'version ', version
    doc_tobe_deleted = getdocdetails(filename,int(version))
    db = getconnection()
    db.delete(doc_tobe_deleted)
    files_list = listalldocuments()
    return render_template('list.html', result_msg="File deleted successfully..!", files_list=files_list)


# below function is used to download the file to the local machine
@app.route('/download/<filename>/<version>')
def download(filename, version):
    print "In Download"
    temp_doc = getdocdetails(filename,int(version))

    db = getconnection()
    file = db.get_attachment(temp_doc,filename)
    file_output = open(str(filename), 'wb')
    print" after file output"
    file_output.write(file.read())
    # print file_output.read()
    file_output.close()
    file_output = open(str(filename), 'rb')
    print"before return"
    return send_file(file_output, as_attachment=True)


# used to get the cloudant connection and return the database obeject
def getconnection():

    cloudantDBURL = 'https://98bf8368-ef0f-4831-8a59-6d24198dd646-bluemix:0ea42785fb10c24ed7ddf846b8b40d76b6efed1c3e14d1b1af857b01690618ba@98bf8368-ef0f-4831-8a59-6d24198dd646-bluemix.cloudant.com'
    username = '98bf8368-ef0f-4831-8a59-6d24198dd646-bluemix'
    password = '0ea42785fb10c24ed7ddf846b8b40d76b6efed1c3e14d1b1af857b01690618ba'
    couch = couchdb.Server(cloudantDBURL)
    couch.resource.credentials = (username, password)
    print "DB connection established"
    # check for the db or create a new one if it does not exist
    try:
        db = couch['karthy_assmt2_filedb1']
    except:
        db = couch.create('karthy_assmt2_filedb1')
        print 'DB created'
    else:
        print 'DB exists'

    return db

# accepts the filename and version number
# return the document associated with them
def getdocdetails(userfilename,userversionnumber):
    db = getconnection()
    for id in db:
        temp_doc = db[id]
        if temp_doc['filename'] == userfilename and temp_doc['version'] == userversionnumber:
            print" this is the file for which document details requested"
            return temp_doc


port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
