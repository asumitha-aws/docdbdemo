"""
DocumentDB Retrieve Lambda Function with Metrics Tracking

This Lambda function retrieves data from DocumentDB and tracks metrics for the operations.
"""

import json
import boto3
import base64
import logging
import os
import pymongo
import ssl
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

@track_operation('Query')
def query_documents(collection, query=None, limit=10):
    """
    Query documents from DocumentDB
    
    Args:
        collection: DocumentDB collection
        query (dict): Query filter
        limit (int): Maximum number of documents to return
    
    Returns:
        list: List of documents
    """
    logger.info(f"Querying documents from collection: {collection.name}")
    
    try:
        if query is None:
            query = {}
        
        # Add operation metrics dimension
        docdb_metrics.add_dimension('Collection', collection.name)
        docdb_metrics.add_dimension('QueryType', 'Find')
        
        cursor = collection.find(query).limit(limit)
        documents = list(cursor)
        
        return documents
    except Exception as e:
        logger.error(f"Error querying documents: {str(e)}")
        raise

@track_operation('Count')
def count_documents(collection, query=None):
    """
    Count documents in DocumentDB
    
    Args:
        collection: DocumentDB collection
        query (dict): Query filter
    
    Returns:
        int: Document count
    """
    logger.info(f"Counting documents in collection: {collection.name}")
    
    try:
        if query is None:
            query = {}
        
        # Add operation metrics dimension
        docdb_metrics.add_dimension('Collection', collection.name)
        docdb_metrics.add_dimension('QueryType', 'Count')
        
        count = collection.count_documents(query)
        
        return count
    except Exception as e:
        logger.error(f"Error counting documents: {str(e)}")
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
    logger.info("Starting DocumentDB retrieve operation with metrics tracking")
    
    try:
        # Get DocumentDB credentials
        credentials = get_credentials()
        username = credentials['username']
        password = credentials['password']
        
        # Get KMS key
        kms_key = get_kms_key()
        
        # Extract query parameters from event
        query_params = event.get('queryStringParameters', {}) or {}
        name_filter = query_params.get('name')
        email_filter = query_params.get('email')
        limit = int(query_params.get('limit', 10))
        
        # Build query
        query = {}
        if name_filter:
            query['name'] = name_filter
        if email_filter:
            query['email'] = email_filter
        
        # Connect to DocumentDB
        client = connect_to_docdb(username, password, 'docdb-demo.cluster-xxxxxxxxxxxx.us-east-1.docdb.amazonaws.com')
        
        # Select database and collection
        db = client['demo']
        collection = db['users']
        
        # Count documents
        count = count_documents(collection, query)
        
        # Query documents
        documents = query_documents(collection, query, limit)
        
        # Close connection
        client.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Documents retrieved successfully',
                'count': count,
                'documents': json.loads(dumps(documents))
            })
        }
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error retrieving documents',
                'error': str(e)
            })
        }

# Original lambda_handler function from DocDBDemoRetrive.zip
def original_lambda_handler(event, context):
    """
    Original Lambda handler function (preserved for reference)
    
    This function should be replaced with the new lambda_handler function above.
    """
    # Implementation would be here
    pass