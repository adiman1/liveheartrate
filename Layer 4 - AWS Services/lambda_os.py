import boto3
import json
import base64
import requests
from requests_aws4auth import AWS4Auth

# AWS region and OpenSearch configuration
region = 'xxxxxxx'  # Replace with your AWS region
service = 'es'
domain = 'https://search-garmin-hr-data-xxxxxxxxxxxxx.region.es.amazonaws.com'
index_name = 'heart_rate'

# Retrieve temporary AWS credentials for SigV4 signing
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

# Set headers for OpenSearch HTTP request
headers = { "Content-Type": "application/json" }

def lambda_handler(event, context):
    """Triggered by Kinesis records; sends decoded data to OpenSearch."""
    
    session = boto3.Session()
    creds = session.get_credentials().get_frozen_credentials()

    # Log diagnostic information
    print("Access Key:", creds.access_key)
    print("Role ARN:", boto3.client('sts').get_caller_identity()['Arn'])
    print("Restarting Lambda")

    # Loop through each record in the incoming Kinesis event
    for record in event['Records']:
        # Step 1: Decode the base64-encoded Kinesis payload
        payload = base64.b64decode(record["kinesis"]["data"])

        # Step 2: Parse the decoded JSON data
        data = json.loads(payload)
        print("Decoded data:", data)

        # Step 3: Construct the OpenSearch document URL
        url = f"{domain}/{index_name}/_doc"

        # Step 4: Send the JSON data to OpenSearch
        response = requests.post(url, auth=awsauth, json=data, headers=headers)

        # Step 5: Log the request status
        print("Sending to URL:", url)
        print("OpenSearch response:", response.status_code, response.text)

    # Return a success response to indicate all records were processed
    return {
        'statusCode': 200,
        'body': json.dumps('Records processed and sent to OpenSearch')
    }
