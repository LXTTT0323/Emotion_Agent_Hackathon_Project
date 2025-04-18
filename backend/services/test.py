import os
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
client = AzureOpenAI(
    api_version="2024-12-01-preview",
    endpoint="https://emotionagentco1241584875.openai.azure.com/",
    credential=AzureKeyCredential("2dZw8VQ9ZBXqd1yXpVO8pFyIYCe1JHsbPSt0Z0m6jJmHFOICEQF6JQQJ99BDACHYHv6XJ3w3AAAAACOGggHR")
)

# import os
# from openai import AzureOpenAI

# endpoint = "https://emotionagentco1241584875.openai.azure.com/"
# model_name = "gpt-4o-mini"
# deployment = "gpt-4o-mini"

# subscription_key = "2dZw8VQ9ZBXqd1yXpVO8pFyIYCe1JHsbPSt0Z0m6jJmHFOICEQF6JQQJ99BDACHYHv6XJ3w3AAAAACOGggHR"
# api_version = "2024-07-18"

# client = AzureOpenAI(
#     api_version=api_version,
#     azure_endpoint=endpoint,
#     api_key=subscription_key,
# )

# response = client.chat.completions.create(
#     messages=[
#         {
#             "role": "system",
#             "content": "You are a helpful assistant.",
#         },
#         {
#             "role": "user",
#             "content": "I am going to Paris, what should I see?",
#         }
#     ],
#     max_tokens=4096,
#     temperature=1.0,
#     top_p=1.0,
#     model=deployment
# )

# print(response.choices[0].message.content)