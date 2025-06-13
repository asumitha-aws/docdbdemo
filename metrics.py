"""
DocumentDB Metrics Tracking Module

This module provides functions to track and publish metrics related to DocumentDB operations.
"""

import time
import logging
import boto3
import json
from datetime import datetime

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize CloudWatch client
cloudwatch = boto3.client('cloudwatch')

class DocumentDBMetrics:
    """Class to handle DocumentDB metrics tracking and publishing"""
    
    def __init__(self, namespace="DocumentDB/Metrics"):
        """
        Initialize the DocumentDBMetrics class
        
        Args:
            namespace (str): CloudWatch namespace for metrics
        """
        self.namespace = namespace
        self.dimensions = [
            {
                'Name': 'Environment',
                'Value': 'Production'
            }
        ]
    
    def add_dimension(self, name, value):
        """
        Add a dimension to metrics
        
        Args:
            name (str): Dimension name
            value (str): Dimension value
        """
        self.dimensions.append({
            'Name': name,
            'Value': value
        })
    
    def track_connection(self, func):
        """
        Decorator to track DocumentDB connection metrics
        
        Args:
            func: The function to wrap
        
        Returns:
            wrapper: The wrapped function
        """
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                logger.error(f"Connection error: {str(e)}")
                raise
            finally:
                end_time = time.time()
                duration = (end_time - start_time) * 1000  # Convert to milliseconds
                
                # Log metrics
                metrics_data = {
                    'ConnectionDuration': duration,
                    'ConnectionSuccess': 1 if success else 0,
                    'ConnectionFailure': 0 if success else 1
                }
                
                self._log_metrics("Connection", metrics_data)
                
                # Publish metrics to CloudWatch
                self._publish_metrics([
                    {
                        'MetricName': 'ConnectionDuration',
                        'Value': duration,
                        'Unit': 'Milliseconds'
                    },
                    {
                        'MetricName': 'ConnectionSuccess',
                        'Value': 1 if success else 0,
                        'Unit': 'Count'
                    },
                    {
                        'MetricName': 'ConnectionFailure',
                        'Value': 0 if success else 1,
                        'Unit': 'Count'
                    }
                ])
        
        return wrapper
    
    def track_operation(self, operation_name):
        """
        Decorator to track DocumentDB operation metrics
        
        Args:
            operation_name (str): Name of the operation (e.g., 'Insert', 'Query')
        
        Returns:
            decorator: The decorator function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                document_count = 0
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    
                    # Try to determine document count from result
                    if hasattr(result, '__len__'):
                        document_count = len(result)
                    elif isinstance(result, dict) and 'count' in result:
                        document_count = result['count']
                    
                    return result
                except Exception as e:
                    logger.error(f"{operation_name} operation error: {str(e)}")
                    raise
                finally:
                    end_time = time.time()
                    duration = (end_time - start_time) * 1000  # Convert to milliseconds
                    
                    # Log metrics
                    metrics_data = {
                        f'{operation_name}Duration': duration,
                        f'{operation_name}Success': 1 if success else 0,
                        f'{operation_name}Failure': 0 if success else 1,
                        f'{operation_name}DocumentCount': document_count
                    }
                    
                    self._log_metrics(operation_name, metrics_data)
                    
                    # Publish metrics to CloudWatch
                    self._publish_metrics([
                        {
                            'MetricName': f'{operation_name}Duration',
                            'Value': duration,
                            'Unit': 'Milliseconds'
                        },
                        {
                            'MetricName': f'{operation_name}Success',
                            'Value': 1 if success else 0,
                            'Unit': 'Count'
                        },
                        {
                            'MetricName': f'{operation_name}Failure',
                            'Value': 0 if success else 1,
                            'Unit': 'Count'
                        },
                        {
                            'MetricName': f'{operation_name}DocumentCount',
                            'Value': document_count,
                            'Unit': 'Count'
                        }
                    ])
            
            return wrapper
        
        return decorator
    
    def _log_metrics(self, operation, metrics_data):
        """
        Log metrics data
        
        Args:
            operation (str): Operation name
            metrics_data (dict): Metrics data to log
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'metrics': metrics_data
        }
        
        logger.info(f"DocumentDB Metrics: {json.dumps(log_data)}")
    
    def _publish_metrics(self, metric_data):
        """
        Publish metrics to CloudWatch
        
        Args:
            metric_data (list): List of metric data dictionaries
        """
        try:
            cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        **metric,
                        'Dimensions': self.dimensions,
                        'Timestamp': datetime.utcnow()
                    } for metric in metric_data
                ]
            )
        except Exception as e:
            logger.error(f"Error publishing metrics to CloudWatch: {str(e)}")

# Create a singleton instance
docdb_metrics = DocumentDBMetrics()

# Convenience functions
def track_connection(func):
    """Decorator to track DocumentDB connection metrics"""
    return docdb_metrics.track_connection(func)

def track_operation(operation_name):
    """Decorator to track DocumentDB operation metrics"""
    return docdb_metrics.track_operation(operation_name)