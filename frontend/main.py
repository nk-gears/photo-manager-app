import os
import random
from google.cloud import storage
from flask import Flask, flash, request, redirect, url_for,send_file
# [START gae_python37_app]
import flask
import six
from flask import jsonify
from werkzeug.utils import secure_filename
import tempfile

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)


#Google Cloud Utility Functions

def _get_storage_client():
  return storage.Client.from_service_account_json('creds.json')

#Utility Methods


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file_to_cloud(randomRequestId,file_stream, filename, content_type):
    print("Uploading file to cloud")
    client = _get_storage_client()
    bucket = client.bucket("photomgr")
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


def renderFromBlobStorage(filename):
    client = _get_storage_client()
    bucket = client.get_bucket("photomgr")
    blob = bucket.blob(filename)
    with tempfile.NamedTemporaryFile() as temp:
        blob.download_to_filename(temp.name)
        return send_file(temp.name, attachment_filename=filename,mimetype='image/jpeg')


@app.route('/render-image')
def render_image():
      req_id=request.args.get("req_id")
      filename=request.args.get("filename")
      mode=request.args.get("mode")
      if(mode=="p"):
        filename=f"req-{req_id}/converted/{filename}"
      if(mode=="o"):
        filename=f"req-{req_id}/{filename}"
      return renderFromBlobStorage(filename)

def blob_exists(bucket_name, filename):
  client = _get_storage_client()
  bucket = client.get_bucket(bucket_name)
  blob = bucket.blob(filename)
  return blob.exists()

@app.route('/api/check-status', methods=['GET'])
def check_status():
      req_id=request.args.get("req_id")
      filename=request.args.get("filename")
      # GO TO GOOGLE STORAGE and check whether the converted folder exists
      actual_filename=f"req-{req_id}/converted/{filename}"
      is_converted=blob_exists("photomgr",actual_filename)
      process_status={"processed":is_converted,"req_id":req_id,"filename":filename}
      return jsonify(process_status)


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
            randomRequestId=random.randint(1, 101)
            blob_filename=save_file_to_cloud(randomRequestId,file.read(),filename, file.content_type)
            #send a message to the Topic
            send_message_to_topic(blob_filename)

            template_values = {"filename":file.filename, "request_id":randomRequestId}
            return flask.render_template('index.html', **template_values)


#if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
app.secret_key = 'secret key'
app.run(host='127.0.0.1', port=8082, debug=True)
# [END gae_python37_app]
