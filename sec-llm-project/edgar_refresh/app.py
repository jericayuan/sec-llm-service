import json
import os
import boto3
import requests
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

USER_AGENT = "Jerica Yuan jxyuan@uci.edu"
url = "https://www.sec.gov/files/company_tickers.json"


def lambda_handler(event, context):
    request_id = context.aws_request_id
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.error(f"[{request_id}] SEC EDGAR returned {response.status_code} for {url}")

            return {
                "error": "SecEdgarError",
                "message": f"SEC EDGAR request failed with status {response.status_code} for {url}"
            }
    except requests.exceptions.RequestException as e:
        logger.error(f"[{request_id}] Network error calling {url}: {e}")
        return {
            "error": "SecEdgarNetworkError",
            "message": f"Failed to reach SEC EDGAR at {url}"
        }

    try:
        s3 = boto3.client('s3')
        s3.put_object(Bucket=os.environ["BUCKET_NAME"], Key="company_tickers.json", Body=response.content)
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(f"[{request_id}] S3 put_object failed ({error_code})")
        return {
            "error": "S3AccessError",
            "message": f"Failed to write to S3: {error_code}"
        }
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}")
        return {
            "error": "InternalError",
            "message": "An unexpected error occurred while refreshing EDGAR data."
        }
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "refreshed",
        }),
    }
