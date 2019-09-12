
#Steps

- Go to Google Cloud Platform
- Click Cloud Shell
- git clone https://github.com/nk-gears/photo-manager-app.git
- cd photo-manager-app
- virtualenv --python python3 ~/envs/photoenv
- source ~/envs/photoenv/bin/activate

- pip install -r requirements.txt
- gcloud app create
- gcloud app deploy app.yaml     --project bk-projects

## Session 3 : 12 Sep 2019
### Upload file to Blob Storage and Sent message to TaskQue

- Create a Bucket in Google Cloud
- Create Service Account
  - https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.0/bk_cloud-data-access/content/gcs-create-service-account.html
- Create PubSub Topic
- Create Subscription Name
