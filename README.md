# Serverless Data Pipeline with AWS Glue, Lambda, and S3 

## Project Overview
This project demonstrates how to build a **serverless data lake** using AWS services such as **S3, Glue, Lambda, SNS**, and **EventBridge (formerly CloudWatch Events)**. The pipeline is designed to transform incoming raw CSV data into Parquet format, which is then stored in an S3 bucket. The process is automated through AWS Glue crawlers and ETL jobs, triggered by S3 events, Lambda functions, and EventBridge rules. Upon successful completion, a notification is sent via SNS.

## Architecture

### High-Level Flow
1. **Raw Data Ingestion**: Raw CSV files are uploaded to an S3 bucket.
2. **Crawler Triggering**: A Lambda function is triggered by S3 notifications to start an AWS Glue crawler.
3. **Glue Crawler**: The Glue crawler catalogs the raw data and creates a schema in the Glue Data Catalog.
4. **ETL Job Triggering**: Upon successful crawler completion, an EventBridge rule triggers another Lambda function to start a Glue ETL job.
5. **ETL Transformation**: The Glue ETL job reads the cataloged data, transforms the CSV files into Parquet format, and stores the results in a target S3 bucket.
6. **Completion Notification**: After successful transformation, an SNS notification is sent to inform about the job's success.

### Architecture Diagram
![](https://github.com/vighneshbuddhivant/Serverless-Data-Lake-Pipeline-with-AWS-Glue-Lambda-S3/blob/02bac742234776f0dd7b9447b3e8fea51d770bb9/glue-lambda-pipeline-arch.png)

---
### Tools and Technologies Used

- **AWS S3**: Used for storing raw CSV data and transformed Parquet files.
- **AWS Lambda**: Automates the triggering of Glue crawlers and ETL jobs.
- **AWS Glue**: Performs data cataloging (via Glue Crawler) and data transformation (via Glue ETL jobs).
- **AWS EventBridge**: Handles event-based triggers for workflow automation, such as starting ETL jobs after the Glue Crawler succeeds.
- **AWS SNS**: Sends email notifications upon successful completion of the ETL job.
- **Python (Boto3)**: Used in Lambda functions to interact with AWS services.
- **AWS IAM**: Provides permissions for Lambda functions to access S3, Glue, and other services.

---

## Detailed Architecture and Workflow

### 1. **S3 Bucket Setup**
- **Bucket Name**: `serverless-glue-lambda-project`
    - `rawcsvstorage/`: Stores raw CSV files.
    - `transformedparquetstorage/`: Stores transformed Parquet files.

### 2. **First Lambda Function: Start Glue Crawler**
This Lambda function is triggered by an S3 notification when a new CSV file is uploaded. It starts a Glue Crawler.

```python
import json
import boto3

glue = boto3.client('glue')

def lambda_handler(event, context):
    response = glue.start_crawler(Name='serverless-glue-lambda-project-crawler')
    return {
        'statusCode': 200,
        'body': json.dumps('Crawler started successfully')
    }
```

### 3. **Glue Crawler**
- **Crawler Name**: `serverless-glue-lambda-project-crawler`
- **Database**: `demotesting`
- This crawler scans the S3 bucket (`rawcsvstorage`) and creates a catalog of the raw data in AWS Glue.

### 4. **Second Lambda Function: Start Glue ETL Job**
Once the Glue crawler completes successfully, a CloudWatch (EventBridge) rule triggers this Lambda function to start the Glue ETL job.

```python
import json
import boto3

def lambda_handler(event, context):
    glue = boto3.client('glue')
    response = glue.start_job_run(JobName="serverless-project-etl-job")
    print("ETL Job Triggered")
```

### 5. **EventBridge Rule (Crawler Completion)**
This EventBridge rule listens for the Glue crawler completion event and triggers the second Lambda function to start the Glue ETL job.

```json
{
  "source": ["aws.glue"],
  "detail-type": ["Glue Crawler State Change"],
  "detail": {
    "state": ["SUCCEEDED"],
    "crawlerName": ["serverless-glue-lambda-project-crawler"]
  }
}
```

### 6. **AWS Glue ETL Job**
The Glue job reads data from the Glue Data Catalog, transforms the CSV data into Parquet format, and writes it to the `transformedparquetstorage` folder in S3.

```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Reading from Glue catalog
datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "demotesting", table_name = "rawcsvstorage", transformation_ctx = "datasource0")

# Writing to S3 in Parquet format
datasink4 = glueContext.write_dynamic_frame.from_options(
    frame = datasource0,
    connection_type = "s3",
    connection_options = {"path": "s3://serverless-glue-lambda-project/transformedparquetstorage/"},
    format = "parquet",
    transformation_ctx = "datasink4"
)

job.commit()
```

### 7. **EventBridge Rule (ETL Job Completion)**
This EventBridge rule listens for the Glue ETL job completion event. If the job is successful, it triggers an SNS notification.

```json
{
  "source": ["aws.glue"],
  "detail-type": ["Glue Job State Change"],
  "detail": {
    "jobName": ["serverless-project-etl-job"],
    "state": ["SUCCEEDED"]
  }
}
```

### 8. **SNS Notification**
- **SNS Topic Name**: `GlueETLJobSuccessNotification`
- **Subscription**: Email protocol to notify about successful ETL job completion.

---

## Conclusion
This project demonstrates how to set up a fully automated **serverless data pipeline** using AWS Glue, Lambda, S3, EventBridge, and SNS. By leveraging these AWS services, we efficiently transform raw CSV data into optimized Parquet format and store it in S3, with real-time notifications for job completion.

