#!/bin/bash

# Load environment variables from the .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

python3.9 -m pip install openai pydantic -t .

# Zip the function code
zip -r function.zip .

# Set function name
FUNCTION_NAME="SentimentAnalyzerFunction"

# Check if the Lambda function exists
if aws lambda get-function --function-name $FUNCTION_NAME >/dev/null 2>&1; then
    echo "Function $FUNCTION_NAME exists. Updating the function code."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://function.zip \
        --architectures arm64 \
        --runtime python3.9
else
    echo "Function $FUNCTION_NAME does not exist. Creating the function."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.9 \
        --role $ROLE_ARN \
        --handler lambda_handler.lambda_handler \
        --zip-file fileb://function.zip \
        --architectures arm64
fi

echo "Operation completed."
