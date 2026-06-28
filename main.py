import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from gmail_service import GmailService
from email_parser import EmailParser
from agents import AIAgents


def log_action(email_id, subject, intent, action):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(f"ID: {email_id} | Subject: {subject} | Intent: {intent} | Action: {action}\n")


def main():
    print("\n" + "="*60)
    print("📧 AI GMAIL SMART REPLY ASSISTANT")
    print("="*60)

    # ✅ NEW: Ask permission before connecting
    connect = input("\nDo you want to connect to Gmail? (yes/no): ").strip().lower()
    if connect not in ["yes", "y"]:
        print("Exiting application...")
        return

    print("\nInitializing Gmail Service...")
    gmail_service = GmailService()

    if not gmail_service.service:
        print("❌ Failed to initialize Gmail API.")
        return

    try:
        print("Initializing AI Agents...")
        ai_agents = AIAgents()
    except Exception as e:
        print(f"❌ Failed to initialize AI Agents. Did you set OPENAI_API_KEY?\nError: {e}")
        return

    print("\nFetching unread emails...")
    messages = gmail_service.get_unread_emails(max_results=5)

    if not messages:
        print("📭 No unread emails found.")
        return

    parsed_emails = []

    # ✅ Improved email display
    print("\n--- Unread Emails ---")
    for idx, msg in enumerate(messages):
        full_msg = gmail_service.get_email_details(msg['id'])
        if full_msg:
            parsed_data = EmailParser.parse(full_msg)
            parsed_emails.append(parsed_data)

            print(f"\n[{idx}]")
            print(f"From   : {parsed_data['sender']}")
            print(f"Subject: {parsed_data['subject']}")

    if not parsed_emails:
        print("❌ Could not fetch email details.")
        return

    while True:
        try:
            choice = input("\nEnter email index to process (or 'q' to quit): ").strip()

            if choice.lower() == 'q':
                print("👋 Exiting application...")
                break

            idx = int(choice)

            if idx < 0 or idx >= len(parsed_emails):
                print("❌ Invalid index. Try again.")
                continue

            selected_email = parsed_emails[idx]

            print("\n" + "="*60)
            print(f"📨 From   : {selected_email['sender']}")
            print(f"📌 Subject: {selected_email['subject']}")
            print("\n📝 Email Content:\n")
            print(selected_email['body'][:800] + "...\n")
            print("="*60)

            print("🤖 Analyzing email and generating reply...\n")

            intent, reply = ai_agents.process_email(
                selected_email['subject'],
                selected_email['body']
            )

            print(f"🔍 Intent Detected: {intent}")

            if intent.lower() == "spam":
                print("⚠️ Spam detected. Skipping email.")
                log_action(selected_email['id'], selected_email['subject'], intent, "Skipped (Spam)")
                continue

            if not selected_email['body'].strip():
                print("⚠️ Email body is empty. Reply may be inaccurate.")

            print("\n--- ✉️ AI Generated Reply ---\n")
            print(reply)
            print("-" * 40)

            # ✅ Action loop
            while True:
                action = input("\nOptions: [y] Send | [e] Edit | [n] Skip: ").strip().lower()

                if action in ['y', 'yes']:
                    print("📤 Sending reply...")
                    success = gmail_service.send_reply(
                        original_message_id=selected_email['id'],
                        to_email=selected_email['sender'],
                        subject=selected_email['subject'],
                        reply_text=reply
                    )

                    if success:
                        print("✅ Reply sent & email marked as read.")
                        gmail_service.mark_as_read(selected_email['id'])
                        log_action(selected_email['id'], selected_email['subject'], intent, "Replied")
                        parsed_emails.pop(idx)
                    else:
                        print("❌ Failed to send reply.")
                        log_action(selected_email['id'], selected_email['subject'], intent, "Send Failed")

                    break

                elif action in ['e', 'edit']:
                    print("\n✏️ Enter your edited reply (press ENTER twice to finish):")
                    lines = []
                    while True:
                        line = input()
                        if not line:
                            break
                        lines.append(line)

                    edited_reply = "\n".join(lines).strip()

                    if edited_reply:
                        reply = edited_reply
                        print("\n--- Updated Reply ---\n")
                        print(reply)
                    else:
                        print("⚠️ Edit cancelled.")

                elif action in ['n', 'no']:
                    print("⏭️ Skipping this email.")
                    log_action(selected_email['id'], selected_email['subject'], intent, "Skipped")
                    break

                else:
                    print("❌ Invalid option.")

        except ValueError:
            print("❌ Please enter a valid number or 'q'.")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()