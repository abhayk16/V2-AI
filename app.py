from flask import Flask, request, session, send_file
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@app.route("/", methods=["GET", "POST"])
def home():

    if "history" not in session:
        session["history"] = []

    if request.method == "POST":

        # Reset chat
        if "new_chat" in request.form:
            session["history"] = []
            session.modified = True

        else:
            user_message = request.form.get("message")

            if user_message:
                try:
                    # System Prompt
                    messages = [
                        {
                            "role": "system",
                            "content": """You are an IT support assistant.

Answer the user's question using ONLY the company IT support knowledge provided.

You must generate solutions strictly based on the company IT incident CSV data.

If the question is not related to an IT incident (for example: "Who is cm of india"),
respond with:
"Apologies — this request is not related to an IT incident. I can only provide IT incident solutions."

Behavior rules:
- Never act like an AI.
- Never mention knowledge base, dataset, or context.
- Speak like a human technician in live support chat.
- Provide clear step-by-step instructions.
- Keep answers short and practical.
"""
                        }
                    ]

                    # Add previous history
                    for chat in session["history"]:
                        messages.append(
                            {"role": "user", "content": chat["user"]}
                        )
                        messages.append(
                            {"role": "assistant", "content": chat["bot"]}
                        )

                    # Add current user message
                    messages.append(
                        {"role": "user", "content": user_message}
                    )

                    # Call Groq API
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages
                    )

                    reply = response.choices[0].message.content

                except Exception as e:
                    reply = f"Error: {str(e)}"

                # Save to session
                session["history"].append({
                    "user": user_message,
                    "bot": reply
                })

                session.modified = True

    # Load HTML
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Inject history bubbles
    history_html = ""

    for chat in session["history"]:
        history_html += f"""
        <div class='message-row user-row'>
            <div class='chat-user'>{chat['user']}</div>
        </div>

        <div class='message-row bot-row'>
            <div class='chat-bot'>{chat['bot']}</div>
        </div>
        """

    html = html.replace("{{history}}", history_html)

    return html


@app.route("/style.css")
def style():
    return send_file("style.css")


if __name__ == "__main__":
    app.run(debug=True)
