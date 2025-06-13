"""
Test script for DocumentDB metrics tracking

This script demonstrates how to use the metrics tracking functionality.
"""

import json
import time
import logging
from metrics import docdb_metrics, track_connection, track_operation

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Mock DocumentDB client and collection
class MockDocDBClient:
    def __init__(self):
        self.connected = True
    
    def close(self):
        self.connected = False

class MockCollection:
    def __init__(self, name):
        self.name = name
        self.documents = [
            {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
            {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'},
            {'id': 3, 'name': 'Bob Johnson', 'email': 'bob@example.com'}
        ]
    
    def insert_one(self, document):
        self.documents.append(document)
        return MockInsertResult()
    
    def find(self, query=None):
        return MockCursor(self.documents)
    
    def count_documents(self, query=None):
        return len(self.documents)

class MockInsertResult:
    def __init__(self):
        self.inserted_id = '123456789'
        self.acknowledged = True

class MockCursor:
    def __init__(self, documents):
        self.documents = documents
    
    def limit(self, limit):
        return self
    
    def __iter__(self):
        return iter(self.documents)

# Test functions with metrics tracking
@track_connection
def test_connect_to_docdb():
    """Test connection to DocumentDB with metrics tracking"""
    logger.info("Testing connection to DocumentDB...")
    time.sleep(0.5)  # Simulate connection time
    return MockDocDBClient()

@track_operation('Insert')
def test_insert_document(collection, document):
    """Test inserting a document with metrics tracking"""
    logger.info(f"Testing insert document into collection: {collection.name}")
    time.sleep(0.3)  # Simulate insert time
    return collection.insert_one(document)

@track_operation('Query')
def test_query_documents(collection, query=None):
    """Test querying documents with metrics tracking"""
    logger.info(f"Testing query documents from collection: {collection.name}")
    time.sleep(0.2)  # Simulate query time
    cursor = collection.find(query)
    return list(cursor)

@track_operation('Count')
def test_count_documents(collection, query=None):
    """Test counting documents with metrics tracking"""
    logger.info(f"Testing count documents in collection: {collection.name}")
    time.sleep(0.1)  # Simulate count time
    return collection.count_documents(query)

def main():
    """Main test function"""
    logger.info("Starting DocumentDB metrics tracking test")
    
    # Add dimensions
    docdb_metrics.add_dimension('TestEnvironment', 'Development')
    
    try:
        # Test connection
        client = test_connect_to_docdb()
        
        # Create mock collection
        collection = MockCollection('users')
        
        # Test count documents
        count = test_count_documents(collection)
        logger.info(f"Document count: {count}")
        
        # Test query documents
        documents = test_query_documents(collection)
        logger.info(f"Query returned {len(documents)} documents")
        
        # Test insert document
        document = {'name': 'Alice Brown', 'email': 'alice@example.com', 'timestamp': time.time()}
        result = test_insert_document(collection, document)
        logger.info(f"Insert result: {result.inserted_id}, acknowledged: {result.acknowledged}")
        
        # Test count documents again
        count = test_count_documents(collection)
        logger.info(f"Document count after insert: {count}")
        
        # Close connection
        client.close()
        
        logger.info("DocumentDB metrics tracking test completed successfully")
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")

if __name__ == "__main__":
    main()