import json
import boto3
from bs4 import BeautifulSoup
from secedgar import  SecEdgar

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

def main():
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

    prompt = "What were Apple's Greater China segment net sales for the fiscal quarter ended June 2026?"
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

    response_body = json.loads(response["body"].read())
    answer_text = response_body["content"][0]["text"]
    print(f"Prompt: {prompt}\n")
    print(f"Response:\n{answer_text}")

if __name__ == "__main__":
    main()