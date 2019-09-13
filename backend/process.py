from PIL import Image
from google.cloud import pubsub_v1
import time
import json
import pathlib
import os
from google.auth import jwt
from google.cloud import storage

project_id="bk-projects"
subscription_name="image-subscribers"
bucket_name="photomgr"

service_account_info = json.load(open("creds.json"))
audience = "https://pubsub.googleapis.com/google.pubsub.v1.Subscriber"

credentials = jwt.Credentials.from_service_account_info(
    service_account_info, audience=audience
)

subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
subscription_path = subscriber.subscription_path(
    project_id, subscription_name)



def convert_image(input_image_path,
    output_image_path):
   color_image = Image.open(input_image_path)
   bw = color_image.convert('L')
   bw.save(output_image_path)
   #converted


def _get_storage_client():
      return storage.Client.from_service_account_json('creds.json')

def process_image(filepath):
    storage_client=_get_storage_client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filepath)

    print("Dowloading file to Local VM instance for processing")
    destination_file_name="/tmp/" + filepath
    local_dir_name=os.path.dirname(destination_file_name)
    pathlib.Path(local_dir_name).mkdir(parents=True, exist_ok=True)
    blob.download_to_filename(destination_file_name)
    converted_path="/tmp/converted/" + filepath
    local_dir_name=os.path.dirname(converted_path)
    pathlib.Path(local_dir_name).mkdir(parents=True, exist_ok=True)
    convert_image(destination_file_name,converted_path)

    #Write the conversion logic later
    return converted_path



def save_processed_file_to_cloud(filepath, filename):
    client = _get_storage_client()
    bucket = client.bucket(bucket_name)
    fileparts=filename.split("/")
    actual_filename=os.path.join(fileparts[0],"converted",fileparts[1])
    # req-22/converted/new-rabbit.jpg
    print("Uploading file to blob")
    print(actual_filename)
    blob = bucket.blob(actual_filename)
    blob.upload_from_filename(filepath)

    return actual_filename

def callback(message):

    print('Received message: {}'.format(message))
    encoding = 'utf-8'
    blob_filepath=message.data.decode(encoding)
    final_processed=process_image(blob_filepath)
    save_processed_file_to_cloud(final_processed, blob_filepath)
    message.ack()



subscriber.subscribe(subscription_path, callback=callback)


print('Listening for messages on {}'.format(subscription_path))
while True:
    time.sleep(60)





#if __name__ == '__main__':
#black_and_white('photo.JPG',
       # 'BWphoto.JPG.jpg')


#TODO
"""
blob-storage :

Source : <username>-12233324234/raw/623432432/photo.JPG
Target : <username>-12233324234/processed/623432432/photo.JPG

- Read the Image Item Name from the Que
- Read the Item from the Cloud Storage based on username
- Convert the BW Image and store them in the bLob under processed

"""
