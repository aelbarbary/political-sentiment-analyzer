import json
import random
import logging
import requests
from datetime import datetime
import os 

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

BACKEND_URL = os.getenv('BACKEND_URL')  # Fetch the environment variable

if not BACKEND_URL:
    logger.error("BACKEND_URL environment variable is not set. Exiting.")
    raise ValueError("BACKEND_URL environment variable is required.")

# List of sample users and channels to simulate Slack environment
USERS = ["U12345", "U67890", "U11111", "U22222"]
CHANNELS = ["C54321", "C98765", "C19283"]

# List of random Slack-like message texts
MESSAGE_TEXTS = [
    "Hello there!",
    "How's it going?",
    "Did you see the latest update?",
    "Can you help with this task?",
    "Reminder: Check the report",
    "Please confirm your availability",
    "Looking forward to the meeting!"
]

# Lambda Handler function triggered by EventBridge or another event
def lambda_handler(event, context):
    """
    AWS Lambda function to simulate sending Slack-like events to a backend.
    This function generates a Slack event and sends it to a backend.
    """
    logger.info("Lambda function triggered by EventBridge")

    # Generate a random Slack-like event
    slack_event = generate_random_slack_message()

    # Forward the event to your backend
    send_to_backend(slack_event)

    # After sending the event, the function ends. EventBridge will trigger it again at the next interval.

def generate_random_slack_message():
    """
    Simulate generating a random Slack message event.
    """
    user = random.choice(USERS)
    channel = random.choice(CHANNELS)
    text = random.choice(MESSAGE_TEXTS)
    timestamp = str(datetime.now().timestamp())  # Use current timestamp as the message timestamp
    
    slack_event = {
        "event": {
            "type": "message",
            "user": user,
            "channel": channel,
            "text": text,
            "ts": timestamp
        }
    }
    
    logger.info(f"Generated Slack event: {json.dumps(slack_event)}")
    return slack_event

def send_to_backend(slack_event):
    """
    Send the simulated Slack event to a backend (via an HTTP POST request).
    """
    try:
        # Send the Slack-like event as an HTTP POST request to your backend
        response = requests.post(BACKEND_URL, json=slack_event)
        
        # Log the response from the backend
        if response.status_code == 200:
            logger.info("Event successfully sent to backend.")
        else:
            logger.error(f"Failed to send event to backend. Status code: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Error sending event to backend: {str(e)}")
