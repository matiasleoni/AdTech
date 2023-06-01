# AdTech architecture implementation

![diagrama](https://github.com/matiasleoni/AdTech/assets/72895418/33babb11-e345-46c5-9c25-9dcc608f71d7)


## Description

* We deployed the necessary architecture for an API to receive web banner advertising requests. The API answers according to a recommendation system. This system gets an everyday update as a consequence of cumulative new information provided by the clients’ web which gets processed with a custom model.
* The recommendation team of the media agency uses the forementioned architecture deployed in AWS using ECS, RDS, EC2 and S3 tools that run the data pipeline and the API.
* The API runs dockerized in an ECS cluster and was programmed with FastAPI. The daily task of updating the recommendations was programmed with AirFlow on an EC2 instance which reads raw data from S3 buckets and updates the recommendation database which is contained in an AWS RDS instance.

## Files

* /EC2: You can find all the files we coppied to the EC2 instance to run the Airflow code
	* It includes the *airflow.cfg* code which should replace the corresponding file after initialization
	* A text file with commands to run in the EC2 instance
	* /Airflow_code : the code to run tasks with Airflow scheduler
* /to_ECS_docker: these are the files that go in the Docker image we create in ECR AWS in order to service the ECS cluster.
	* It includes de *Dockerfile* for the image
	* the requirements to pip in the file system
	* /app: the code to run the API
* /mockDatabase: some files to manipulate and test AWS RDS service with Psycopg2 library using SQL locally.
* /to_s3: the "client" click and views data (simulated) that should be uploaded in an S3 buckets
* ECS_FASTAPI_instructions.md : a tutorial to run the ECR and ECS services
* readme.me : this file



