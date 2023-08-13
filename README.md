# Cryptocurrency anomaly detection - v0.0.1

## Table of Contents

1. [Project Description](#description)
2. [Files Description](#files)
3. [Running Files](#running)
4. [Orchestration](#orchestration)
5. [Project Benefits](#benefits)
6. [Licensing and Authors](#licensingandauthors)
***

## Project Description <a name="description"></a>

In the realm of finance, understanding and identifying anomalies—unusual patterns or events—is a critical task for maintaining stability and making informed decisions. This project aims to harness the power of data analytics to detect anomalies within financial data obtained from Yahoo Finance. The primary focus lies in utilizing the concept of amplitude, calculated as the difference between the closing and opening prices of financial instruments. By identifying anomalies in these amplitude values, this project offers insights into potentially noteworthy market events that may justify further investigation. 

**The workflow includes the following steps:**

* Data Collection: Retrieve data from the Yahoo finance API using the provided endpoints.

* Data Storage: Store collected data in S3 bucket with layered transformations using best practices. 

* Business data: Business transformations go to the datawarehouse.

* Anomaly Detection: The heart of the project revolves around anomaly detection. By analyzing the amplitude values, statistical methods will be employed to determine the normal   behavior of the financial instruments. Any amplitude value that significantly deviates from this expected behavior will be marked as an anomaly.

* Insight and Decision Support: The final goal of the project is to provide actionable insights. Identified anomalies could point towards specific events or market conditions that demand attention. These insights can aid financial professionals in making well-informed decisions and adopting proactive strategies.

![architecture]()

The entire project is orchestrated by AWS fargate which will be explained in more detail in the orchestration section.
***

## Files Description <a name="files"></a>

* `template.yaml`: AWS cloud formation instance template to create RDS, ECS with fargate and S3 services, integrating all of them.

* `main.py`: Main file to orchestrate all the components that are in the folder `components/`.

* `components/`: Directory containing the modularized components for the project.

    * `get_api_data.py`: Python module to collect data from Yahoo finance API and read them as pandas dataframe.
    * `create_s3_raw.py`: Python module to move the raw data that arrived from Yahoo finance API to the raw layer.
    * `create_s3_processed.py`: Python module to move data from raw layer to processed layer (performing some basic transformations).
    * `dw_management.py`: Python module to manage everything about the datawarehouse that is: create schema, table and download/upload data.
    * `anomaly_detection_system.py`: Python module that serves to obtain data from the DW, perform some necessary procedures to feed the anomaly detection model. Finally, the inference is made.
    * `alert_system.py`: Python module to send an email to those responsible.

* `tests/`: directory that contains the tests for the functions that are in `components/`.

    * `conftest.py`: File where the fixtures were created to feed the unit tests.

* `.env`: File containing environment variables used in the project.

* `dockerfile`: File with instructions for creating the application's docker image.

* `model_card.md`: File that contains detailed and specific documentation about the model used to perform the inferences.

* `requirements.txt`: File containing packages needed for the application to work.
***

## Running Files Locally <a name="running"></a>

To run the project, follow these steps:

### Clone the repository

Go to [cryptocurrency_anomaly_detection](https://github.com/vitorbeltrao/cryptocurrency_anomaly_detection) and click on Fork in the upper right corner. This will create a fork in your Github account, i.e., a copy of the repository that is under your control. Now clone the repository locally so you can start working on it:

`git clone https://github.com/[your_github_username]/cryptocurrency_anomaly_detection.git`

and go into the repository:

`cd cryptocurrency_anomaly_detection` 

### Create AWS account

Go to the [AWS](https://aws.amazon.com/) page and create a free account for you to use the services needed for the project.

### template.yaml File

Go to the [cloud formation](https://aws.amazon.com/cloudformation/) instance on AWS and upload this template so that the S3, database and ECS services are created to start the pipeline.

### functions folder

After performing the above steps, you can run `python main.py` in your terminal and all components will run in the required order until the final inference is performed

### .env File

To make everything work, you need to create the `.env` file in each subfolder of the **functions** folder.

In the .env, you must define all necessary variables like usernames, passwords and anything else that is sensitive information for your project.

**Here is the list of variables that must be passed:**

* For the alert system (send email to those responsible): you must pass the outgoing email, the arrival email and the password acquired by gmail.

* For DW (RDS postgres instance): endpoint name, port, database name, user, password, schema name, temporary schema name (you should pass this one with the same name as the main schema, just prefixing it with "temp_"), table name.

* For S3 bucket instance: bucket name, source directory, AWS access key id, AWS secret access secret, region name.

### Testing

- Run the tests:

    `pytest`

    The tests of the functions used are in the `cryptocurrency_anomaly_detection/tests` folder and to run them just write the code above in the terminal. In that folder are the tests that cover the production functions that are in the `cryptocurrency_anomaly_detection/components/` folder.

    In progress...
***

## Orchestration <a name="orchestration"></a>

In progress...
***

## Project Benefits <a name="benefits"></a>

* **Early Detection of Market Events:** By monitoring amplitude anomalies, the project enhances the ability to identify potentially impactful market events at an early stage.

* **Data-Driven Decision-Making:** The project empowers financial experts to base their decisions on data-driven insights, thereby mitigating risks and capitalizing on opportunities.

* **Automated Monitoring:** The automated anomaly detection process allows for continuous monitoring of financial data, ensuring swift responses to unexpected events.

* **Enhanced Risk Management:** Timely anomaly detection contributes to improved risk management strategies, reducing the potential impact of market disruptions.

* **Learning from Historical Data:** Analysis of historical anomalies can facilitate learning about past market dynamics, potentially aiding in predicting similar patterns in the future.
***

## Licensing and Author <a name="licensingandauthors"></a>

Vítor Beltrão - Data Scientist

Reach me at: 

- vitorbeltraoo@hotmail.com

- [linkedin](https://www.linkedin.com/in/v%C3%ADtor-beltr%C3%A3o-56a912178/)