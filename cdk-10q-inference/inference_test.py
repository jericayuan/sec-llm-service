import json
import boto3
from bs4 import BeautifulSoup
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)
from secedgar.secedgar import SecEdgar

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
QUESTION = "What were Apple's Greater China segment net sales for the fiscal quarter ended June 2026?"

def extract_relevant_section(text, keyword="Segment Operating Performance", window=3000):
    idx = text.find(keyword)
    if idx == -1:
        print(f"Warning: '{keyword}' not found, using first {window} chars instead")
        return text[:window]
    return text[idx:idx + window]

def main():
    se = SecEdgar('https://www.sec.gov/files/company_tickers.json')
    cik, ticker, title = se.ticker_to_cik('AAPL')
    filing = se.quarterly_filing(cik, 2026, "Q3")
    print(f"Using filing: {filing}")

    raw_html = se.get_filing_text(filing["cik"], filing["accessionNumber"], filing["primaryDocument"])
    full_text = BeautifulSoup(raw_html, "html.parser").get_text()

    relevant_text = extract_relevant_section(full_text)

    prompt = (
        "Using the information below, answer the following quesetion.\n\n"
        f"Question: {QUESTION}\n\n"
        f"Document:\n{relevant_text}"
    )

    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

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