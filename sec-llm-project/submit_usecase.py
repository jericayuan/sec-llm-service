import boto3
import json

bedrock = boto3.client("bedrock", region_name="us-east-1")

form_data = {
    "companyName": "MLT",
    "companyWebsite": "https://github.com/jericayuan",
    "intendedUsers": "0",  
    "industryOption": "Education",
    "otherIndustryOption": "",
    "useCases": "Educational coursework project: a serverless AWS Lambda application that answers questions about SEC filings using Claude via Amazon Bedrock."
}

response = bedrock.put_use_case_for_model_access(
    formData=json.dumps(form_data)
)

print(response)