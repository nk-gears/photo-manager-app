import os
import random
from google.cloud import storage
from flask import Flask, flash, request, redirect, url_for
# [START gae_python37_app]
import flask
import six
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



#Google Cloud Utility Functions

def _get_storage_client():
  return storage.Client.from_service_account_json('creds.json')

#Utility Methods


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file_to_cloud(file_stream, filename, content_type):
    print("Uploading file to cloud")
    client = _get_storage_client()
    bucket = client.bucket("photomgr")
    randomRequestId=random.randint(1, 101)
    actual_filename=f"req-{randomRequestId}/{filename}"
    blob = bucket.blob(actual_filename)
    blob.upload_from_string(
        file_stream,
        content_type=content_type)
    url = blob.public_url
    if isinstance(url, six.binary_type):
        url = url.decode('utf-8')
    return actual_filename




@app.route('/')
def index():
    template_values = {
        'title': "Photo Manager"}
    return flask.render_template('index.html', **template_values)


def send_message_to_topic(actualBlob_path):
  from google.cloud import pubsub_v1
  publisher = pubsub_v1.PublisherClient()
  topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id="bk-projects",
    topic='image-process-topic')
  publisher.publish(topic_name, str.encode(actualBlob_path))

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'photofile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['photofile']
        print(request.files)
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            blob_filename=save_file_to_cloud(file.read(),filename, file.content_type)
            #send a message to the Topic
            send_message_to_topic(blob_filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "file uploaded. Please wait for sometime for the file to get processed."


#if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
app.secret_key = 'secret key'
app.run(host='127.0.0.1', port=8082, debug=True)
# [END gae_python37_app]
