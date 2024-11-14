import json
import os
import requests
import logging
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)
api_key = os.getenv("OPENAI_API_KEY")

# Define the OpenAI API URL for the chat completion endpoint
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

def process_message(text):
    try:
        prompt = (
            f"Classify the following message. Respond with one of the following options:\n"
            f"- If the message is political, respond with: 'Political: Sentiment: [score]' where score is between -10 (very negative) and 10 (very positive).\n"
            f"- If the message is not political, respond with: 'Not Political'.\n\n"
            f"Message: \"{text}\""
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4",  # or use "gpt-3.5-turbo" if preferred
            "messages": [
                {"role": "system", "content": "You are an assistant that classifies political messages and analyzes their sentiment."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150
        }

        # Send the POST request to the OpenAI API
        response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
        logger.info(f"Request sent to OpenAI API: {json.dumps(payload)}")
        logger.info(f"Received response status code: {response.status_code}")
        
        # Check if the response was successful
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Response from OpenAI API: {json.dumps(result)}")
            
            # Extract response content
            response_content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

            logger.info(f"Response content: {response_content}")
            
            # Process the result
            if response_content.lower().startswith("political"):
                # Extract sentiment score from the response
                sentiment_score = int(response_content.split("Sentiment:")[1].strip().split()[0])
                return {"is_political": True, "sentiment_score": sentiment_score}
            else:
                # If the message is not political
                return {"is_political": False, "sentiment_score": 0}
        else:
            print(f"Error: Received {response.status_code} from OpenAI API")
            return {"is_political": False, "sentiment_score": 0}

    except Exception as e:
        print(f"Error processing message: {e}")
        return {"is_political": False, "sentiment_score": 0}

def lambda_handler(event, context):
    output_records = []
    
    for record in event['Records']:
        try:
            # Extract the base64-encoded data
            encoded_data = record.get('kinesis', {}).get('data', '')
            
            # Check if the data is empty
            if not encoded_data:
                logger.warning(f"Empty data field in record: {record}")
                continue  # Skip this record if no data
            
            # Decode the base64-encoded data
            try:
                decoded_data = base64.b64decode(encoded_data).decode('utf-8')
                logger.info(f"Decoded data: {decoded_data}")
            except Exception as e:
                logger.error(f"Base64 decode failed for record: {record} - Error: {e}")
                continue  # Skip this record if decoding fails
            
            # Parse the decoded data as JSON
            try:
                payload = json.loads(decoded_data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON for record: {record} - Error: {e}")
                continue  # Skip this record if JSON decoding fails
            
            # Process the message (assuming the message has 'text' field)
            message_text = payload.get('text', '')
            result = process_message(message_text)

            # Attach the result to the payload
            payload['is_political'] = result['is_political']
            payload['sentiment_score'] = result['sentiment_score']
            
            # Add the processed record to the output list
            output_records.append({
                'Data': json.dumps(payload)
            })
        
        except Exception as e:
            logger.error(f"Unexpected error processing record: {record} - Error: {e}")
    
    return {'Records': output_records}
