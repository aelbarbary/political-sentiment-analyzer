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
    
    try:
        # Parse the 'body' field from the event, as it contains the Slack event data as a JSON string
        body = event.get('body')
        if body:
            # Load the body as JSON
            slack_event_body = json.loads(body)
            slack_event = slack_event_body.get('event')

            # Check if 'event' is present
            if slack_event:
                send_to_kinesis(slack_event)
                return {
                    "statusCode": 200,
                    "body": json.dumps({"message": "Event successfully processed and sent to Kinesis Firehose"})
                }
            else:
                logger.error("No 'event' key found in the Slack event body.")
                logger.error(slack_event_body)
                return {
                    "statusCode": 400,
                    "body": json.dumps({"message": "Missing 'event' key in the payload"})
                }
        else:
            logger.error("No 'body' found in the incoming request.")
            logger.error(event)
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "No body found in the request"})
            }

    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from 'body'.")
        logger.error(event)
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid JSON in request body"})
        }

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