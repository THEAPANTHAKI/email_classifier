import pandas as pd
from langdetect import detect
from openai import AzureOpenAI

# AI

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint="https://theap-madml99h-eastus2.cognitiveservices.azure.com/",
    api_key="5ymS2hEfEggWKjLUxIjvzrz5lzaTQBLwJliMXLYb3RZ4ASNEhcXiJQQJ99BEACHYHv6XJ3w3AAAAACOGiAVd"
)

model = "gpt-4.1"

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


#LANG

def detect_language_local(text):
    try:
        return detect(str(text))
    except Exception:
        return "unknown"

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
    except Exception:
        return "error"

# PROCESSING

df = pd.read_csv("email_dataset.csv")
df.columns = df.columns.str.strip()


df['Content'] = df['Content'].astype(str).str.strip()
df = df[df['Content'].notna() & (df['Content'] != '')]

df['language'] = ''
df['intent'] = ''

for index, row in df.iterrows():
    content = str(row['Content']).strip()

    language = detect_language_local(content)
    intent = classify_intent(content)

    df.at[index, 'language'] = language
    df.at[index, 'intent'] = intent

    print(f"Row {index + 1} done.")

df.to_csv("email_classified_output.csv", index=False)

print("All emails processed. Results saved to 'email_classified_output.csv'.")
