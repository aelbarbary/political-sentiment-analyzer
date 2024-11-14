import json
import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key) 

def process_message(text):
    try:
        prompt = (
            f"Classify the following message. Respond with one of the following options:\n"
            f"- If the message is political, respond with: 'Political: Sentiment: [score]' where score is between -10 (very negative) and 10 (very positive).\n"
            f"- If the message is not political, respond with: 'Not Political'.\n\n"
            f"Message: \"{text}\""
        )

        # Use client.chat.completions.create for OpenAI API v1.0+ (chat models)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an assistant that classifies political messages and analyzes their sentiment."},
                {"role": "user", "content": prompt}
            ],
            model="gpt-4",  # Or gpt-3.5-turbo if preferred
            max_tokens=150
        )

        print(response)
        # Access the content of the response correctly
        result = response.choices[0].message.content.strip()

        # Process the result
        if result.lower().startswith("political"):
            # Extract sentiment score from the response
            sentiment_score = int(result.split("Sentiment:")[1].strip().split()[0])
            return {"is_political": True, "sentiment_score": sentiment_score}
        else:
            # If the message is not political, return the result
            return {"is_political": False, "sentiment_score": 0}
        


    except Exception as e:
        print(f"Error processing message: {e}")
        return {"is_political": False, "sentiment_score": 0} 

def lambda_handler(event, context):
    output_records = []
    
    for record in event['Records']: 
        payload = json.loads(record['kinesis']['data'])
        
        message_text = payload.get('text', '')
        result = process_message(message_text)

        # Attach the result to the payload
        payload['is_political'] = result['is_political']
        payload['sentiment_score'] = result['sentiment_score']
        
        # Add the processed record to the output list
        output_records.append({
            'Data': json.dumps(payload)
        })
    
    return {'Records': output_records}