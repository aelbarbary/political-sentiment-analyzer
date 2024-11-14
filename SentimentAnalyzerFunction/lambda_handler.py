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
        f"\n\nGuidelines: A message is considered political if it refers to political figures, political parties, elections, government policies, or political movements. If the message expresses political opinions or endorsements, it should be classified as political."
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
    logger.info(f"Received json event: {json.dumps(event)}")
    
    # Ensure we're iterating over 'records' (not 'Records')
    for record in event['records']:
        # Decode the base64-encoded 'data' field
        record_data = base64.b64decode(record['data']).decode('utf-8')
        
        # Parse the decoded record data as JSON
        try:
            payload = json.loads(record_data)
        except json.JSONDecodeError:
            logger.error(f"Error decoding record data: {record_data}")
            continue
        
        message_text = payload.get('text', '')
        if message_text:
            # Process the message through OpenAI API for classification
            result = process_message(message_text)

            # Attach the result to the payload
            payload['is_political'] = result['is_political']
            payload['sentiment_score'] = result['sentiment_score']
        
            # Add the processed record to the output list
            output_records.append({
                'recordId': record['recordId'],
                "result": "Ok",
                'data': base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')
            })
        else:
            logger.error(f"Message text not found in record: {record_data}")

    # Return the processed records
    return {'records': output_records}
