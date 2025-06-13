# DocumentDB Demo with Metrics Tracking

This project demonstrates how to use Amazon DocumentDB with Lambda functions for inserting and retrieving data, with added metrics tracking functionality.

## Overview

The project includes:

1. CloudFormation template for deploying the infrastructure
2. Lambda functions for inserting and retrieving data from DocumentDB
3. Metrics tracking module for monitoring DocumentDB operations

## Metrics Tracking

The metrics tracking functionality captures the following metrics:

### Connection Metrics
- **ConnectionDuration**: Time taken to establish a connection to DocumentDB (milliseconds)
- **ConnectionSuccess**: Count of successful connections (1 or 0)
- **ConnectionFailure**: Count of failed connections (1 or 0)

### Operation Metrics
- **InsertDuration**: Time taken to insert documents (milliseconds)
- **InsertSuccess**: Count of successful insert operations (1 or 0)
- **InsertFailure**: Count of failed insert operations (1 or 0)
- **InsertDocumentCount**: Number of documents inserted

- **QueryDuration**: Time taken to query documents (milliseconds)
- **QuerySuccess**: Count of successful query operations (1 or 0)
- **QueryFailure**: Count of failed query operations (1 or 0)
- **QueryDocumentCount**: Number of documents retrieved

- **CountDuration**: Time taken to count documents (milliseconds)
- **CountSuccess**: Count of successful count operations (1 or 0)
- **CountFailure**: Count of failed count operations (1 or 0)

### Dimensions
The metrics include the following dimensions:
- **Environment**: Production
- **Host**: DocumentDB host
- **Collection**: DocumentDB collection name
- **QueryType**: Type of query (Find, Count)

## How to Use

### Packaging Lambda Functions

1. Install the required dependencies:
   ```
   pip install boto3 pymongo -t ./package
   ```

2. Copy the Lambda function files and metrics module:
   ```
   cp DocDBDemoInsert.py package/
   cp DocDBDemoRetrive.py package/
   cp metrics.py package/
   ```

3. Create the ZIP files:
   ```
   cd package
   zip -r ../DocDBDemoInsert.zip .
   zip -r ../DocDBDemoRetrive.zip .
   ```

4. Upload the ZIP files to your S3 bucket:
   ```
   aws s3 cp DocDBDemoInsert.zip s3://your-bucket-name/
   aws s3 cp DocDBDemoRetrive.zip s3://your-bucket-name/
   ```

### Deploying the CloudFormation Stack

Deploy the CloudFormation stack using the AWS Management Console or AWS CLI:

```
aws cloudformation deploy \
  --template-file DocDBDemo.json \
  --stack-name docdb-demo \
  --parameter-overrides \
    KeyAliasName=docdbdemokey \
    DBClusterName=docdb-demo \
    DBInstanceName=docdb-instance \
    DocDBMasterUser=dbadmin \
    DocDBMasterPassword=YourPassword \
    DBInstanceClass=db.t3.medium \
    LambdaCodeS3BucketNameLocation=your-bucket-name \
    InsertLambdaZipFileName=DocDBDemoInsert.zip \
    RetrieveLambdaZipFileName=DocDBDemoRetrive.zip \
    LambdaLayerZipFileName=lambda-layer.zip \
    ec2KeyPairName=your-key-pair \
    YourIPAddress=your-ip-address/32
```

### Viewing Metrics

You can view the metrics in the CloudWatch console:

1. Open the CloudWatch console
2. Navigate to Metrics
3. Select the "DocumentDB/Metrics" namespace
4. View the metrics by dimension (Environment, Host, Collection, QueryType)

## Logging

The metrics are also logged to CloudWatch Logs in a structured JSON format:

```json
{
  "timestamp": "2023-06-01T12:34:56.789Z",
  "operation": "Insert",
  "metrics": {
    "InsertDuration": 123.45,
    "InsertSuccess": 1,
    "InsertFailure": 0,
    "InsertDocumentCount": 1
  }
}
```

You can use CloudWatch Logs Insights to query and analyze the metrics logs.
