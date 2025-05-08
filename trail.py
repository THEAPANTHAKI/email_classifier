from langdetect import detect
from openai import AzureOpenAI

# Info
email_id = "thea@gmail.com"
email_content = "I want to close my loan. Please let me know the process."

print("Email ID:", email_id)
print("Content:", email_content)

# Lang
def detect_language_local(text):
    try:
        return detect(str(text))
    except Exception:
        return "unknown"

language = detect_language_local(email_content)
print("Detected Language:", language)

# AI 
client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint="https://theap-madml99h-eastus2.cognitiveservices.azure.com/",  
    api_key="5ymS2hEfEggWKjLUxIjvzrz5lzaTQBLwJliMXLYb3RZ4ASNEhcXiJQQJ99BEACHYHv6XJ3w3AAAAACOGiAVd"
)

print("Azure OpenAI client initialized.")

model = "gpt-4.1" 

# prompt
persona = (
    "You are an AI assistant trained to classify customer emails for a loan company. "
    "Your ONLY possible output choices are exactly these categories: "
    "'New Loan Inquiry', 'Loan Closure', 'Repayment Issue', 'Document Submission', 'Interest Rate Query', 'General Query'. "
    "Read the following customer email carefully and choose ONLY one category from the list above. "
    "Do not explain your choice or provide any extra text. Output only the category name. "
    "Here are the keyword-based rules to help you classify: "
    "If the email mentions words like 'new', 'apply', 'application', 'open' → choose 'New Loan Inquiry'. "
    "If it mentions 'close', 'closure', 'terminate', 'cancel' → choose 'Loan Closure'. "
    "If it mentions 'payment', 'repayment', 'receipt', 'due', 'pay' → choose 'Repayment Issue'. "
    "If it mentions 'document', 'form', 'upload', 'submission' → choose 'Document Submission'. "
    "If it mentions 'interest rate', 'rate', 'APR' → choose 'Interest Rate Query'. "
    "If none of these apply or you're unsure → choose 'General Query'."
)

# Classification 
def classify_intent(content):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": persona},
                {"role": "user", "content": content}
            ],
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error calling Azure OpenAI:", e)
        return "error"


intent = classify_intent(email_content)
print("Detected Intent:", intent)
