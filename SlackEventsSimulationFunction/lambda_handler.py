import json
import random
import logging
import requests
from datetime import datetime
import os 

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BACKEND_URL = os.getenv('BACKEND_URL')  

if not BACKEND_URL:
    logger.error("BACKEND_URL environment variable is not set. Exiting.")
    raise ValueError("BACKEND_URL environment variable is required.")

USERS = ["U12345", "U67890", "U11111", "U22222"]
CHANNELS = ["C54321", "C98765", "C19283"]

MESSAGE_TEXTS = [
    "I think the new president is going to make real change. Exciting times ahead!",
    "I can't believe this new administration. It's going to be a disaster for the country.",
    "This political shift is exactly what we need to move forward. Hopeful for the future.",
    "Honestly, I'm really worried about where the country is headed with this new leadership.",
    "We need to stay united and support the new president. Change takes time.",
    "I can't stand the new policies. I feel like everything is going downhill fast.",
    "I’m optimistic about the changes, but I know many aren’t on board yet.",
    "The direction this country is taking under the new president is frightening. We need to push back.",
    "It’s refreshing to see someone finally take charge and make bold decisions.",
    "I just don’t get how anyone can support this administration. It’s hard to stay positive."
]

def lambda_handler(event, context):
    logger.info("Lambda function triggered by EventBridge")
    slack_event = generate_random_slack_message()
    send_to_backend(slack_event)

def generate_random_slack_message():
    user = random.choice(USERS)
    channel = random.choice(CHANNELS)
    text = random.choice(MESSAGE_TEXTS)
    timestamp = str(datetime.now().timestamp())
    
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
    try:
        response = requests.post(BACKEND_URL, json=slack_event)
        
        if response.status_code == 200:
            logger.info("Event successfully sent to backend.")
        else:
            logger.error(f"Failed to send event to backend. Status code: {response.status_code}")
    
    except Exception as e:
        logger.error(f"Error sending event to backend: {str(e)}")
