import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scope
SCOPES = ['https://mail.google.com/']


class GmailService:
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        # ✅ FIX: Always use absolute path
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        self.credentials_path = os.path.join(BASE_DIR, credentials_path)
        self.token_path = os.path.join(BASE_DIR, token_path)

        print("📂 Looking for credentials at:", self.credentials_path)

        self.service = self.authenticate()

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load token if exists
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If no valid credentials → login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"❌ credentials.json not found at {self.credentials_path}")

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('gmail', 'v1', credentials=creds)
            print("✅ Gmail service initialized successfully!")
            return service
        except HttpError as error:
            print(f'❌ Error during authentication: {error}')
            return None

    def get_unread_emails(self, max_results=10):
        """Get unread emails"""
        if not self.service:
            print("❌ Gmail service not initialized.")
            return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX', 'UNREAD'],
                maxResults=max_results
            ).execute()

            return results.get('messages', [])
        except HttpError as error:
            print(f'❌ Error fetching emails: {error}')
            return []

    def get_email_details(self, msg_id):
        """Get full email content"""
        if not self.service:
            return None

        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            return message
        except HttpError as error:
            print(f'❌ Error fetching email details: {error}')
            return None

    def send_reply(self, original_message_id, to_email, subject, reply_text):
        """Send reply email"""
        if not self.service:
            return False

        try:
            message = EmailMessage()
            message.set_content(reply_text)

            message['To'] = to_email

            # Ensure subject starts with "Re:"
            if not subject.lower().startswith('re:'):
                subject = f"Re: {subject}"
            message['Subject'] = subject

            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')

            # Get thread ID
            original_msg = self.service.users().messages().get(
                userId='me',
                id=original_message_id,
                format='minimal'
            ).execute()

            thread_id = original_msg.get('threadId')

            body = {'raw': raw_message}

            if thread_id:
                body['threadId'] = thread_id

            sent = self.service.users().messages().send(
                userId='me',
                body=body
            ).execute()

            print(f"✅ Reply sent successfully! Message ID: {sent['id']}")
            return True

        except HttpError as error:
            print(f'❌ Error sending reply: {error}')
            return False

    def mark_as_read(self, msg_id):
        """Mark email as read"""
        if not self.service:
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

            print("📩 Email marked as read.")
            return True

        except HttpError as error:
            print(f'❌ Error marking email as read: {error}')
            return False