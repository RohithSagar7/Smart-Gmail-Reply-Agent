from dotenv import load_dotenv
import streamlit as st
import re

# ✅ Load environment variables
load_dotenv(dotenv_path=".env")

from gmail_service import GmailService
from email_parser import EmailParser
from agents import AIAgents

st.set_page_config(
    page_title="AI Gmail Assistant",
    layout="wide"
)

st.title("📧 Smart Gmail Reply Agent")

# =========================
# 🔹 Helper Functions
# =========================

def clean_email_body(text):

    # Remove links
    text = re.sub(r'https?://\S+', '', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()[:1500]


def is_noreply(sender):

    sender = sender.lower()

    return any(
        x in sender
        for x in [
            "noreply",
            "no-reply",
            "donotreply"
        ]
    )


def is_sensitive(body):

    body = body.lower()

    sensitive_keywords = [
        "otp",
        "verification code",
        "one time password",
        "login code",
        "security code",
        "password reset",
        "verify your identity",
        "bank account",
        "confidential",
        "authentication code"
    ]

    return any(
        x in body
        for x in sensitive_keywords
    )


def is_spam(body):

    body = body.lower()

    spam_keywords = [
        "unsubscribe",
        "buy now",
        "limited offer",
        "click here",
        "win",
        "free offer",
        "lottery",
        "claim reward"
    ]

    return any(
        x in body
        for x in spam_keywords
    )


# =========================
# 🔹 Initialize Services
# =========================

try:

    if "gmail_service" not in st.session_state:
        st.session_state.gmail_service = GmailService()

    if "ai_agents" not in st.session_state:
        st.session_state.ai_agents = AIAgents()

    gmail_service = st.session_state.gmail_service
    ai_agents = st.session_state.ai_agents

except Exception as e:

    st.error(f"❌ Setup Error: {str(e)}")

    st.stop()


# =========================
# 🔹 Load Emails
# =========================

if st.button("🔄 Load Unread Emails"):

    with st.spinner("Fetching unread emails..."):

        st.session_state.messages = gmail_service.get_unread_emails(
            max_results=25
        )


# =========================
# 🔹 Process Emails
# =========================

if "messages" in st.session_state:

    messages = st.session_state.messages

    parsed_emails = []
    email_options = []

    valid_count = 0

    for msg in messages:

        try:

            full_msg = gmail_service.get_email_details(msg['id'])

            parsed = EmailParser.parse(full_msg)

            sender = parsed.get('sender', '').strip()
            subject = parsed.get('subject', '').strip()
            body = parsed.get('body', '').strip()

            # 🔴 Skip completely empty emails
            if not subject and not body:
                continue

            # 🔴 Fix empty subject
            if not subject:
                subject = "(No Subject)"

            # 🔴 Skip no-reply mails
            if is_noreply(sender):
                continue

            # 🔴 Skip spam
            if is_spam(body):
                continue

            cleaned_body = clean_email_body(body)

            parsed['clean_body'] = cleaned_body
            parsed['subject'] = subject

            parsed_emails.append(parsed)

            email_options.append(
                f"{sender} - {subject}"
            )

            valid_count += 1

            # ✅ Show only top 5 useful emails
            if valid_count >= 5:
                break

        except Exception as e:

            print("Email Parsing Error:", e)

    # =========================
    # 🔹 Display Emails
    # =========================

    if not email_options:

        st.warning("⚠️ No useful unread emails found.")

    else:

        st.success("✅ Showing top 5 useful unread emails")

        selected = st.selectbox(
            "📥 Select Email",
            email_options
        )

        if selected:

            index = email_options.index(selected)

            email = parsed_emails[index]

            st.subheader("📨 Email Content")

            st.write(email['clean_body'])

            # =========================
            # 🔹 Sensitive Mail Detection
            # =========================

            sensitive_mail = is_sensitive(
                email['clean_body']
            )

            if sensitive_mail:

                st.warning(
                    "⚠️ Sensitive email detected.\n\n"
                    "AI reply generation disabled "
                    "for security reasons."
                )

            else:

                # =========================
                # 🔹 Generate Reply
                # =========================

                if st.button("🤖 Generate Reply"):

                    with st.spinner(
                        "Generating AI reply..."
                    ):

                        reply = ai_agents.process_email(
                            email['subject'],
                            email['clean_body']
                        )

                        st.session_state.reply = reply

                # =========================
                # 🔹 Show Generated Reply
                # =========================

                if "reply" in st.session_state:

                    reply = st.session_state.reply

                    edited_reply = st.text_area(
                        "✏️ Edit Reply Before Sending",
                        reply,
                        height=220
                    )

                    # =========================
                    # 🔹 Send Reply
                    # =========================

                    if st.button("📤 Send Reply"):

                        with st.spinner(
                            "Sending reply..."
                        ):

                            success = gmail_service.send_reply(
                                original_message_id=email['id'],
                                to_email=email['sender'],
                                subject=email['subject'],
                                reply_text=edited_reply
                            )

                            if success:

                                gmail_service.mark_as_read(
                                    email['id']
                                )

                                st.success(
                                    "✅ Reply Sent Successfully!"
                                )

                            else:

                                st.error(
                                    "❌ Failed to send reply"
                                )