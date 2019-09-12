
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

