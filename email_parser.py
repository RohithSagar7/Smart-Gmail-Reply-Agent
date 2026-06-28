import base64
import re
from bs4 import BeautifulSoup


class EmailParser:

    @staticmethod
    def extract_body(payload):

        body = ""

        # 🔹 If multipart email
        if 'parts' in payload:
            for part in payload['parts']:

                mime_type = part.get("mimeType")

                # ✅ Plain text
                if mime_type == "text/plain":
                    data = part['body'].get('data')

                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')

                        return body

                # ✅ HTML fallback
                elif mime_type == "text/html":
                    data = part['body'].get('data')

                    if data:
                        html = base64.urlsafe_b64decode(data).decode('utf-8')

                        soup = BeautifulSoup(html, "html.parser")

                        return soup.get_text(separator=" ")

        # 🔹 Single-part email
        else:
            data = payload.get('body', {}).get('data')

            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        return body.strip()

    @staticmethod
    def parse(message):

        payload = message['payload']
        headers = payload.get('headers', [])

        subject = ""
        sender = ""

        for header in headers:
            name = header.get('name')

            if name == "Subject":
                subject = header.get('value')

            elif name == "From":
                sender = header.get('value')

        # 🔥 Extract actual email body
        body = EmailParser.extract_body(payload)

        # 🔹 Clean extra spaces
        body = re.sub(r'\s+', ' ', body)

        return {
            "id": message['id'],
            "sender": sender,
            "subject": subject,
            "body": body
        }