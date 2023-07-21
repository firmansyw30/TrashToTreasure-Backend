
# Trash To Treasure Backend

[![Logo-1.png](https://i.postimg.cc/J4F84jSt/Logo-1.png)](https://postimg.cc/SJc3gYSp)

This is a repository for Trash To Treasure Machine Learning API


## Authors

- [Firmansyah Wicaksono - c220dsx2706 - CC43 Bangkit 2023](https://www.github.com/firmansyw30)


## Installation / Requirement

Make sure you have installed python, check your python using cmd using 

```bash
  python --version
```

and if you don't have python, please click this link to download latest version of [python](https://www.python.org/downloads/)

## Run Locally

Clone the project in your code editor

```bash
  git clone https://github.com/TrashtoTreasure/TrashToTreasure-Backend.git
```

Go to the project directory (this is example directory, and maybe different)

```bash
  cd TrashToTreasure-Backend
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Because in this source code using streaming process for the machine learning model to google cloud storage, make sure you <b>replace </b> this example with your actual services & storage

- Replace with your actual path of generated service account file in json format from google cloud services & make sure the services account is have access to google cloud storage
```bash
  service_account = 'credential/artful-guru-386801-9390336d684c.json'
```
- Replace with your actual bucket name and machine learning model path in google cloud storage (in this case, the machine learning team giving 'h5' format file)
```bash
  bucket_name = 't2t-bucket'
  model_...._path = 'models/model_....h5'
```

After replaced, you can run the code in your directories using this syntax on your terminal
```bash
  python main.py
```
You can test for each endpoint on the postman in the 'main.py' file and if necessary, <b modify </b> this syntax like this
```bash
  if __name__ == '__main__':
    app.run(port=4000, debug=True)
```

## Cloud Architecture

We use additional services like "Firebase" for creating a secure authentication and based on the complexity of configuring the authentication. The authentication is configured by Mobile Development Division.

[![cloud-architecture-product-capstone-project-bangkit-2023-Fix-yang-ini.png](https://i.postimg.cc/fRsGb5Bz/cloud-architecture-product-capstone-project-bangkit-2023-Fix-yang-ini.png)](https://postimg.cc/bs6CCx7W)


## Deployment

To deploy this (native) flask app to google cloud run, please follow this step

- Make sure the necessary configuration like service account, path of each resources and anything else is correct
- Modify this syntax in the 'main.py' like this to make this application is accessable to public
```bash
  if __name__ == '__main__':
    app.run(port=4000, host="0.0.0.0", debug=True)
```
- Upload or clone the code you want to deploy to cloud shell editor
- Change your working directory to your actual directory of the code
```bash
  cd [your-working-directory-of-the-code]
```
- Make sure you create a file in the root directory called "Dockerfile", and write the syntax like this
```bash
  # Use the official lightweight Python image.
  # https://hub.docker.com/_/python
  FROM python:3.11-slim
  
  # Allow statements and log messages to immediately appear in the logs
  ENV PYTHONUNBUFFERED True
  
  # Copy local code to the container image.
  ENV APP_HOME /app
  WORKDIR $APP_HOME
  COPY . ./
  
  # Install production dependencies.
  RUN pip install -r requirements.txt
  RUN pip install gunicorn
  # Run the web service on container startup. Here we use the gunicorn
  # webserver, with one worker process and 8 threads.
  # For environments with multiple CPU cores, increase the number of workers
  # to be equal to the cores available.
  # Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
  CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
  CMD ["python", "main.py"]
```
- Click at the "Cloud Code" button at the bottom https://im4.ezgif.com/tmp/ezgif-4-83a68abae1.gif (detail explanation)
- After clicked, make sure you configure as you needed and make sure it correct, like port based on the code and etc https://im4.ezgif.com/tmp/ezgif-4-180e7c2898.gif (detail explanation)
- And then click deploy, it will automatically create an image based on Dockerfile (in this case)
## Documentation

Click at this link for the API [Documentation](https://documenter.getpostman.com/view/20981294/2s93sf1VrG)


## Tech Stack

**Client:** Visual Studio Code, Cloud Shell Editor, Postman, Cloud Storage and etc

**Server:** Flask


## Lessons Learned

Because this is my first time created an backend using python, managing team too. So this is a great and challenging story for me specially in capstone project at Bangkit 2023


## Feedback

If you have any feedback or critism, please reach out to firmansyahwicaksono30@gmail.com

Student ID : 
c220dsx2706@bangkit.academy - Firmansyah Wicaksono - CC 43

## Evaluation

- The Machine Learning Code not adding validation object, like if we scan the bottle image on glass category the Machine Learning Code will detect it as a glass not a bottle
