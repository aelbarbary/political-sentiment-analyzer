import json
import logging
import boto3
import os
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FIREHOSE_STREAM_NAME = os.getenv('FIREHOSE_STREAM_NAME')

if not FIREHOSE_STREAM_NAME:
    logger.error("FIREHOSE_STREAM_NAME environment variable is not set. Exiting.")
    raise ValueError("FIREHOSE_STREAM_NAME environment variable is required.")

kinesis_client = boto3.client('firehose')

def lambda_handler(event, context):
    logger.info("Lambda function triggered by Slack event")
    
    # Assuming the incoming event is the Slack message
    slack_event = event.get('event')
    if slack_event:
        send_to_kinesis(slack_event)
    else:
        logger.error("No 'event' found in the incoming request.")

def send_to_kinesis(slack_event):
    try:
        response = kinesis_client.put_record(
            DeliveryStreamName=FIREHOSE_STREAM_NAME,
            Record={'Data': json.dumps(slack_event)}
        )
        print("Response from Kinesis Firehose:", response)
        logger.info("Event successfully sent to Kinesis Firehose.")
    except Exception as e:
        logger.error(f"Failed to send event to Kinesis Firehose: {str(e)}")