# AI Email Assistant (Gmail + OpenAI)

An intelligent AI-powered email assistant that connects to your Gmail inbox, classifies incoming emails, and automatically drafts replies for important messages.

---

## Features

* Securely connects to your Gmail account using OAuth2
* Fetches recent emails from your inbox
* Classifies emails into:

  * `spam`
  * `ad`
  * `informational`
  * `normal`
* Automatically generates replies **only for important ("normal") emails**
* Outputs structured JSON for easy downstream use
* Cleans and extracts readable text from HTML emails

---

## Architecture Overview

1. **Gmail API Integration**

   * Authenticates using OAuth2
   * Fetches recent emails
   * Extracts subject, sender, and body

2. **Email Parsing**

   * Decodes base64 email content
   * Uses BeautifulSoup to strip HTML and extract text

3. **AI Processing (OpenAI)**

   * Uses function calling to fetch emails dynamically
   * Classifies each email
   * Generates replies only when necessary

4. **Structured Output**

   * Returns results in JSON format for easy integration

---

## Project Structure

```
.
├── main.py                # Main script
├── credentials.json      # Google OAuth credentials
├── token.pickle          # Saved user auth token
├── API.env               # Environment variables (OpenAI API key)
└── README.md             # Project documentation
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-email-assistant.git
cd ai-email-assistant
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

If you don’t have a requirements file, install manually:

```bash
pip install openai google-api-python-client google-auth-httplib2 \
google-auth-oauthlib beautifulsoup4 python-dotenv
```

---

### 3. Set Up Environment Variables

Create a file named `API.env`:

```env
KEY=your_openai_api_key_here
```

---

### 4. Enable Gmail API

1. Go to Google Cloud Console
2. Create a project
3. Enable **Gmail API**
4. Create OAuth credentials
5. Download and save as:

```
credentials.json
```

---

### 5. Run the Script

```bash
python main.py
```

* On first run, a browser window will open for Gmail authentication
* A `token.pickle` file will be generated for future sessions

---

## How It Works

### Step 1: Tool Definition

The model is given access to a function:

```python
fetch_gmail_inbox()
```

### Step 2: Function Calling

The AI decides when to call the Gmail tool to fetch emails.

### Step 3: Email Processing

Each email is:

* Parsed
* Cleaned
* Structured

### Step 4: AI Classification + Reply

The model returns:

```json
[
  {
    "sender": "...",
    "subject": "...",
    "classification": "normal",
    "reply": "Generated response"
  }
]
```

---

## Example Output

```json
[
  {
    "sender": "recruiter@company.com",
    "subject": "Interview Invitation",
    "classification": "normal",
    "reply": "Thank you for reaching out. I would be happy to schedule an interview..."
  },
  {
    "sender": "promo@store.com",
    "subject": "50% OFF SALE",
    "classification": "ad",
    "reply": null
  }
]
```

---

## Security Notes

* OAuth tokens are stored locally (`token.pickle`)
* Do NOT commit:

  * `credentials.json`
  * `token.pickle`
  * `API.env`

Add them to `.gitignore`:

```
credentials.json
token.pickle
API.env
```

---

## Future Improvements

* Gmail label automation (auto-archive spam/ads)
* Web dashboard for viewing classified emails
* CI/CD pipeline integration
* Support for multiple email providers
* Fine-tuned classification model
* Email priority scoring

---

## Tech Stack

* Python
* OpenAI API (GPT-4o-mini)
* Gmail API
* BeautifulSoup
* OAuth2 Authentication

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

* Google Gmail API
* OpenAI API
* BeautifulSoup for HTML parsing

---


---
