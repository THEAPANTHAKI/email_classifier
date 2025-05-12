import pandas as pd
from langdetect import detect
from openai import AzureOpenAI

# AI Client
client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint="https://theap-madml99h-eastus2.cognitiveservices.azure.com/",
    api_key="5ymS2hEfEggWKjLUxIjvzrz5lzaTQBLwJliMXLYb3RZ4ASNEhcXiJQQJ99BEACHYHv6XJ3w3AAAAACOGiAVd"
)

model = "gpt-4.1"

# --- PROMPTS ---

# Intent
persona = (
    "You are a loan support AI assistant. Your job is to classify the customer's email into exactly one of the following predefined categories:\n\n"
    "- New Loan Inquiry\n"
    "- Loan Closure\n"
    "- Repayment Issue\n"
    "- Interest Rate Query\n"
    "- Document Submission\n"
    "- Loan Status Update\n"
    "- Prepayment Request\n"
    "- Part-Payment Request\n"
    "- Balance Transfer Request\n"
    "- Top-Up Loan Request\n"
    "- Loan Statement Request\n"
    "- Loan Eligibility Check\n"
    "- Co-Applicant or Guarantor Issue\n"
    "- Loan Rejection Appeal\n"
    "- General Query\n\n"
    "Read the email carefully and output ONLY the exact category name from the list above. "
    "Do NOT explain your choice or add any extra text. "
    "If the email content is unclear or doesn't match any category, return 'General Query'."
)

# Loan Type
loan_type_persona = (
    "You are a loan support AI assistant. Based on the email content, classify the loan type involved. "
    "Choose ONLY one from the following:\n\n"
    "- Home Loan\n"
    "- Vehicle Loan / Auto Loan\n"
    "- Loan Against Property\n"
    "- Gold Loan\n"
    "- Loan Against Securities\n"
    "- Loan Against Fixed Deposit\n"
    "- Commercial Property Loan\n"
    "- Construction Loan\n"
    "- Personal Loan\n"
    "- Education Loan\n"
    "- Travel Loan\n"
    "- Medical Loan\n"
    "- Wedding Loan\n"
    "- Consumer Durable Loan\n"
    "- Credit Card Loan\n"
    "- Business Loan\n"
    "- Working Capital Loan\n"
    "- Machinery Loan\n"
    "- Invoice Financing\n"
    "- MSME Loan\n"
    "- SME Loan\n"
    "- Startup Loan\n"
    "- Commercial Vehicle Loan\n"
    "- Agriculture Loan\n"
    "- Student Loan\n"
    "- NRI Loan\n"
    "- Debt Consolidation Loan\n"
    "- Overdraft Facility\n"
    "- Bridge Loan\n"
    "- Top-Up Loan\n"
    "- Emergency Loan\n\n"
    "Output ONLY the name of the loan type. If not clear, respond with 'General Loan'."
)

# Sub-process
subprocess_persona = (
    "You are a loan assistant AI. Classify the customer's email content into one of the following sub-process categories:\n\n"
    "- Account Opening\n"
    "- Account Closure\n"
    "- Disbursement\n"
    "- Foreclosure\n"
    "- Collection Process\n"
    "- Payment Handling\n"
    "- Refund Request\n"
    "- Charges & Fees\n"
    "- Loan Restructuring\n"
    "- Feedback or Complaint\n"
    "- Legal Related\n"
    "- Settlement\n"
    "- Document Submission\n"
    "- Recovery\n"
    "- Loan Status Check\n"
    "- Co-applicant or Guarantor Issues\n"
    "- Eligibility Check\n"
    "- Statement Request\n"
    "- General Sub-process\n\n"
    "Return ONLY the exact sub-process from this list. If unclear, return 'General Sub-process'."
)

# Message Type (query/request/etc.)
message_type_persona = (
    "You are a customer support classifier. Based on the tone and content of the email, classify it into one of these types:\n\n"
    "- Query\n"
    "- Request\n"
    "- Complaint\n"
    "- Feedback\n"
    "- Technical Issue\n"
    "- General Communication\n\n"
    "Return ONLY the type. Do not explain or add anything else."
)

# --- FUNCTIONS ---

def detect_language_local(text):
    try:
        return detect(str(text))
    except Exception:
        return "unknown"

def classify_intent(content):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": persona}, {"role": "user", "content": content}],
            temperature=0,
            top_p=1
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "error"

def classify_loan_type(content):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": loan_type_persona}, {"role": "user", "content": content}],
            temperature=0,
            top_p=1
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "General Loan"

def classify_subprocess(content):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": subprocess_persona}, {"role": "user", "content": content}],
            temperature=0,
            top_p=1
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "General Sub-process"

def classify_message_type(content):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": message_type_persona}, {"role": "user", "content": content}],
            temperature=0,
            top_p=1
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "General Communication"

# --- PROCESSING ---

df = pd.read_csv("email_dataset.csv")
df.columns = df.columns.str.strip()
df['Content'] = df['Content'].astype(str).str.strip()
df = df[df['Content'].notna() & (df['Content'] != '')]

df['language'] = ''
df['intent'] = ''
df['loan_type'] = ''
df['sub_process'] = ''
df['message_type'] = ''

for index, row in df.iterrows():
    content = str(row['Content']).strip()

    language = detect_language_local(content)
    intent = classify_intent(content)
    loan_type = classify_loan_type(content)
    sub_process = classify_subprocess(content)
    message_type = classify_message_type(content)

    df.at[index, 'language'] = language
    df.at[index, 'intent'] = intent
    df.at[index, 'loan_type'] = loan_type
    df.at[index, 'sub_process'] = sub_process
    df.at[index, 'message_type'] = message_type

    print(f"Row {index + 1} done.")

df.to_csv("email_classified_output.csv", index=False)
print("All emails processed. Results saved to 'email_classified_output.csv'.")
