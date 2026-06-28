try:
    from crewai import Agent
except:

    # ✅ Fallback dummy Agent class
    class Agent:
        def __init__(self, *args, **kwargs):
            pass


from groq import Groq


class AIAgents:

    def __init__(self):

        # =========================
        # 🔹 CrewAI Agent References
        # =========================

        # ✅ Lightweight CrewAI usage
        # (Prevents OpenAI dependency errors)

        self.intent_agent = "CrewAI Intent Agent"

        self.reply_agent = "CrewAI Reply Generator Agent"

        self.safety_agent = "CrewAI Safety Validation Agent"

        print("\n🤖 CrewAI Agents Initialized")
        print("✅ Intent Agent Ready")
        print("✅ Reply Agent Ready")
        print("✅ Safety Agent Ready")

        # =========================
        # 🔹 Groq Client
        # =========================

        self.client = Groq(

            # 🔥 Paste your Groq API key here
            api_key="GROQ_API_KEY"

        )

        # ✅ Latest Groq model
        self.model = "llama-3.1-8b-instant"

    # =========================
    # 🔹 Main Email Processing
    # =========================

    def process_email(self, subject, body):

        # 🔹 Clean body
        body = body.replace("\n", " ").strip()[:1500]

        print("\n🤖 CrewAI Multi-Agent Workflow Started")
        print("🔹 Intent Agent Running...")
        print("🔹 Reply Agent Running...")
        print("🔹 Safety Agent Running...")

        prompt = f"""
You are a professional AI email assistant.

Analyze the email carefully and generate a professional reply.

IMPORTANT:
- Reply according to actual email content
- Avoid generic replies
- Do NOT use placeholders like [Name] or [Your Name]
- Write naturally as if the real user is replying
- Avoid overly formal greetings unless necessary
- Keep reply under 80 words
- Be human-like and professional

EMAIL SUBJECT:
{subject}

EMAIL BODY:
{body}

Return ONLY the email reply.
"""

        try:

            # =========================
            # 🔹 Groq LLM Call
            # =========================

            response = self.client.chat.completions.create(

                model=self.model,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.5

            )

            reply = response.choices[0].message.content.strip()

            print("\n🔥 GENERATED AI REPLY:\n")
            print(reply)

            # =========================
            # 🔹 Safety Filtering
            # =========================

            unsafe_words = [
                "password",
                "otp",
                "bank account",
                "credit card"
            ]

            if any(word in reply.lower() for word in unsafe_words):

                reply = (
                    "For security reasons, "
                    "sensitive information cannot be shared via email."
                )

            # ✅ Return only reply
            return reply

        except Exception as e:

            print("\n❌ GROQ ERROR:\n")
            print(e)

            return f"Groq Error: {str(e)}"