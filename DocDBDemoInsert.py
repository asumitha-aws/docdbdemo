"""
DocumentDB Insert Lambda Function with Metrics Tracking

This Lambda function inserts data into DocumentDB and tracks metrics for the operations.
"""

import json
import boto3
import base64
import logging
import os
import pymongo
import ssl
import time
from bson.json_util import dumps
from metrics import docdb_metrics, track_connection, track_operation

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize clients
secretsmanager = boto3.client('secretsmanager')

def get_credentials():
    """
    Get DocumentDB credentials from Secrets Manager
    
    Returns:
        dict: DocumentDB credentials
    """
    secret_name = os.environ.get('docdbCredentials', 'demo/DocumentDB/dbcredential')
    
    try:
        secret_response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret = json.loads(secret_response['SecretString'])
        return secret
    except Exception as e:
        logger.error(f"Error retrieving DocumentDB credentials: {str(e)}")
        raise

def get_kms_key():
    """
    Get KMS key ARN from Secrets Manager
    
    Returns:
        str: KMS key ARN
    """
    secret_name = os.environ.get('kms_key_alias', 'demo/DocumentDB/keyalias')
    
    try:
        secret_response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret = json.loads(secret_response['SecretString'])
        return secret['DocDBDemoKeyArn']
    except Exception as e:
        logger.error(f"Error retrieving KMS key: {str(e)}")
        raise

@track_connection
def connect_to_docdb(username, password, host):
    """
    Connect to DocumentDB
    
    Args:
        username (str): DocumentDB username
        password (str): DocumentDB password
        host (str): DocumentDB host
    
    Returns:
        pymongo.MongoClient: DocumentDB client
    """
    logger.info("Connecting to DocumentDB...")
    
    try:
        client = pymongo.MongoClient(
            host=host,
            port=27017,
            username=username,
            password=password,
            ssl=True,
            ssl_ca_certs='/opt/python/rds-combined-ca-bundle.pem',
            replicaSet='rs0',
            readPreference='secondaryPreferred',
            retryWrites=False
        )
        
        # Add connection metrics dimension
        docdb_metrics.add_dimension('Host', host)
        
        return client
    except Exception as e:
        logger.error(f"Error connecting to DocumentDB: {str(e)}")
        raise

@track_operation('Insert')
def insert_document(collection, document):
    """
    Insert a document into DocumentDB
    
    Args:
        collection: DocumentDB collection
        document (dict): Document to insert
    
    Returns:
        dict: Result of the insert operation
    """
    logger.info(f"Inserting document into collection: {collection.name}")
    
    try:
        result = collection.insert_one(document)
        
        # Add operation metrics dimension
        docdb_metrics.add_dimension('Collection', collection.name)
        
        return {
            'inserted_id': str(result.inserted_id),
            'acknowledged': result.acknowledged
        }
    except Exception as e:
        logger.error(f"Error inserting document: {str(e)}")
        raise

def lambda_handler(event, context):
    """
    Lambda handler function
    
    Args:
        event (dict): Lambda event
        context (object): Lambda context
    
    Returns:
        dict: Response with status code and body
    """
    logger.info("Starting DocumentDB insert operation with metrics tracking")
    
    try:
        # Get DocumentDB credentials
        credentials = get_credentials()
        username = credentials['username']
        password = credentials['password']
        
        # Get KMS key
        kms_key = get_kms_key()
        
        # Extract data from event
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        
        # Connect to DocumentDB
        client = connect_to_docdb(username, password, 'docdb-demo.cluster-xxxxxxxxxxxx.us-east-1.docdb.amazonaws.com')
        
        # Select database and collection
        db = client['demo']
        collection = db['users']
        
        # Insert document
        document = {
            'name': body.get('name', 'Unknown'),
            'email': body.get('email', 'unknown@example.com'),
            'timestamp': time.time()
        }
        
        result = insert_document(collection, document)
        
        # Close connection
        client.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Document inserted successfully',
                'result': result
            })
        }
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error inserting document',
                'error': str(e)
            })
        }

# Original lambda_handler function from DocDBDemoInsert.zip
def original_lambda_handler(event, context):
    """
    Original Lambda handler function (preserved for reference)
    
    This function should be replaced with the new lambda_handler function above.
    """
    # Implementation would be here
    pass