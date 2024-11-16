import boto3
import json
import logging
from collections import defaultdict
from datetime import datetime
from unittest.mock import Mock

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3 = boto3.client('s3')

def process_file(bucket_name, file_key):
    """Process a single file in S3 and aggregate sentiment scores by hour."""
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    lines = response['Body'].read().decode('utf-8').splitlines()
    
    positive_count = 0
    negative_count = 0
    
    for line in lines:
        message = json.loads(line)
        
        if 'sentiment_score' in message :
            sentiment_score = message['sentiment_score']
            
            # Determine if score is positive or negative
            if sentiment_score > 0:
                positive_count += 1
            elif sentiment_score < 0:
                negative_count += 1
    
    return positive_count, negative_count

def aggregate_data(bucket_name):
    """Recursively aggregate sentiment scores by hour from all files in the S3 bucket."""
    aggregated_data = defaultdict(lambda: {'positive': 0, 'negative': 0})

    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get('Contents', []):
            file_key = obj['Key']
            
            try:
                
                year, month, day, hour, filename = file_key.split('/')[-5:]
                positive_count, negative_count = process_file(bucket_name, file_key)
                
                hour_key = f'{year}-{month}-{day}T{hour}:00:00Z'
                
                aggregated_data[hour_key]['positive'] += positive_count
                aggregated_data[hour_key]['negative'] += negative_count
                
                logger.info(f'Processed file {file_key} for {hour_key}')
                
            except Exception as e:
                logger.error(f"Failed to process {file_key}: {str(e)}")
    
    result = [
        {"timestamp": hour_key, "positive": values['positive'], "negative": values['negative']}
        for hour_key, values in aggregated_data.items()
    ]
    
    return result

def lambda_handler(event, context):
    """Lambda handler function."""
    bucket_name = 'political-sentiment-conversations'

    logger.info(f"Starting aggregation for bucket: {bucket_name}")
    aggregated_data = aggregate_data(bucket_name)

    logger.info(f"Aggregated Data: {json.dumps(aggregated_data, indent=2)}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(aggregated_data, indent=2)
    }
