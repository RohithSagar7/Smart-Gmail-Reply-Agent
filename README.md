# Gmail Smart Reply Agent

## Overview

Gmail Smart Reply Agent is an AI-powered email assistant that automatically reads unread Gmail messages, analyzes their content, generates professional email replies using a Large Language Model (LLM), and allows users to review the generated response before sending it.

The project integrates the Gmail API with AI to automate email management while keeping the user in control of the final response.

---

## Features

* Gmail API authentication using OAuth 2.0
* Read unread Gmail messages
* Extract sender, subject, and email body
* AI-generated professional email replies
* Human review before sending replies
* Automatically mark processed emails as read
* Safety checks to avoid sharing sensitive information

---

## Tech Stack

* Python
* Gmail API
* Google OAuth 2.0
* Groq LLM
* CrewAI (lightweight workflow)
* Python Dotenv

---

## Project Structure

```
app.py
main.py
agents.py
gmail_service.py
email_parser.py
requirements.txt
README.md
.env.example
```

---

## Installation

1. Clone the repository

```
git clone https://github.com/YOUR_USERNAME/Gmail-Smart-Reply-Agent.git
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Create a `.env` file

```
GROQ_API_KEY=your_groq_api_key
```

4. Download Gmail OAuth credentials from Google Cloud Console.

5. Save the OAuth file as `credentials.json`.

6. Run the application

```
python app.py
```

---

## Security

The following files are intentionally excluded from GitHub:

* `.env`
* `credentials.json`
* `token.json`

These files contain private credentials and must be created locally.

---

## Future Enhancements

* Multi-language email replies
* Spam email classification
* Email priority prediction
* Attachment summarization
* Support for multiple LLM providers

---

## Author

**Rohith Sagar**

AI & Machine Learning Engineer
