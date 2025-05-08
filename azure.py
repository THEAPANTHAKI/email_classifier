import os   
from openai import AzureOpenAI

endpoint = "https://theap-madml99h-eastus2.cognitiveservices.azure.com/"
model_name = "gpt-4.1"
deployment = "gpt-4.1"

subscription_key = "5ymS2hEfEggWKjLUxIjvzrz5lzaTQBLwJliMXLYb3RZ4ASNEhcXiJQQJ99BEACHYHv6XJ3w3AAAAACOGiAVd"
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "is there going to be a war bet india and pakistan",
        }
    ],
    max_tokens=4096,
    temperature=1.0,
    top_p=1.0,
    model=deployment
)

print(response.choices[0].message.content)