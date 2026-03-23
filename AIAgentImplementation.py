import os
import json
import pickle
import base64
from openai import OpenAI
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv("API.env")

client = OpenAI (api_key=os.getenv("KEY"))

# 1. Define the tool for the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_gmail_inbox",
            "description": "Connects to Gmail to retrieve the latest messages from the user's inbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "The number of recent emails to fetch."
                    }
                },
                "required": []
            }
        }
    }
]

def fetch_gmail_inbox(max_results=10, credentials_file='credentials.json', token_file='token.pickle', scopes=['https://www.googleapis.com/auth/gmail.readonly']):
    """Authenticates and fetches recent emails."""
    creds = None
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    def _extract_recursive(payload):
        if payload.get("body") and payload["body"].get("data"):
            return payload["body"]["data"]
        if payload.get("parts"):
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    return part["body"]["data"]
            for part in payload["parts"]:
                if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
                    return part["body"]["data"]
            for part in payload["parts"]:
                data = _extract_recursive(part)
                if data: return data
        return None

    results = service.users().messages().list(userId='me', maxResults=max_results, q="label:INBOX").execute()
    messages_data = results.get('messages', [])
    all_emails = []

    for msg in messages_data:
        message = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = message.get("payload", {})
        headers = payload.get("headers", [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown Sender")

        raw_data = _extract_recursive(payload)
        body_text = ""
        
        if raw_data:
            try:
                decoded = base64.urlsafe_b64decode(raw_data).decode("utf-8", errors="ignore")
                soup = BeautifulSoup(decoded, "html.parser")
                body_text = soup.get_text(separator=" ", strip=True)
            except Exception:
                body_text = "[Error decoding content]"
        else:
            body_text = "[No body content]"

        all_emails.append({
            "sender": sender,
            "subject": subject,
            "body": body_text
        })

    return all_emails

# --- EXECUTION FLOW ---

messages = [
    {
    "role": "system",
    "content": """
You are an AI email assistant.

For each email provided:
1. Classify it as one of:
   - "spam"
   - "ad"
   - "normal"
   - "informational"

2. If classification is "normal":
   - Draft a professional, concise reply.

3. If classification is "spam" or "ad" or "informational":
   - Do not draft a reply.

Return your response in JSON format like this:

[
  {
    "sender": "...",
    "subject": "...",
    "classification": "spam | ad | normal | informational",
    "reply": "text or null"
  }
]
"""
},
    {"role": "user", "content": "Fetch my 10 most recent emails, classify them, and draft replies only for the normal ones."}
]

# Step 1: Send the conversation and available tools to the model

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

response_message = response.choices[0].message
messages.append(response_message) # Append assistant's message (containing tool_calls)

# Step 2: Check if the model wants to call a function
if response_message.tool_calls:
    for tool_call in response_message.tool_calls:
        if tool_call.function.name == "fetch_gmail_inbox":
            # Correctly handle potential empty arguments
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the local function
            print(f"Executing tool: {tool_call.function.name} with args {function_args}...")
            function_response = fetch_gmail_inbox(**function_args)

            # Step 3: Send the function result back to the model
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "fetch_gmail_inbox",
                "content": json.dumps(function_response),
            })

    # Step 4: Get a final response from the model now that it has the email data
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    print("\n--- Final Output ---\n")
    print(final_response.choices[0].message.content)
else:
    print("The model did not call a function.")