import json

import os
import boto3
import requests

USER_AGENT = "Jerica Yuan jxyuan@uci.edu"

def lambda_handler(event, context):
    headers = {"User-Agent": USER_AGENT}
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=headers)
    
    s3 = boto3.client('s3')
    s3.put_object(Bucket=os.environ["BUCKET_NAME"], Key="company_tickers.json", Body=response.content)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "refreshed",
        }),
    }
