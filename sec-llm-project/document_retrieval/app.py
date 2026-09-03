import json
import os
import boto3
import requests
import logging
import time
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


MODEL_ID = os.environ["MODEL_ID"]
VALID_PERIODS = ["Q1", "Q2", "Q3", "Q4", "FY"]

def lambda_handler(event, context):
    request_id = context.aws_request_id

    question = event.get("question")
    ticker = event.get("ticker")
    year = event.get("year")
    period = event.get("period")

    if period not in VALID_PERIODS:
        return {
            "error": "ValidationError",
            "message": f"Invalid value for 'period': '{period}'. Must be one of: Q1, Q2, Q3, Q4, FY."
        }
    
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    prompt = (
        f"You are answering a question about {ticker}'s {period} {year} SEC filing.\n\n"
        f"Question: {question}\n\n"
        f"Answer based on what you know. If you don't have the actual filing text, explicitly say so instead of guessing specific numbers"
    )
    try:
        start_time = time.time()

        response = bedrock.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            })
        )
        latency_ms = int((time.time() - start_time) * 1000)
        response_body = json.loads(response["body"].read())
        answer_text = response_body["content"][0]["text"]
        input_tokens = response_body["usage"]["input_tokens"]
        output_tokens = response_body["usage"]["output_tokens"]
        return {
            "answer": answer_text,
            "meta": {
                "model": MODEL_ID,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms
            }
        }
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logger.error(f"[{request_id}] Bedrock ClientError ({error_code}) for ticker={ticker}, year={year}, period={period}: {e}")
        return {
            "error": "BedrockInvocationError",
            "message": f"Model invocation failed: {error_code}"
        }
    except Exception as e: 
        logger.error(f"[{request_id}] Unexpected error for ticker={ticker}, year={year}, period={period}: {e}") 
        return { "error": "InternalError", "message": "An unexpected error occurred while processing the request." }