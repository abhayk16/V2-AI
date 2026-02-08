from flask import Flask, request, session, send_file, redirect, url_for
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

WEBSITE_USERNAME = os.getenv("WEBSITE_USERNAME")
WEBSITE_PASSWORD = os.getenv("WEBSITE_PASSWORD")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == WEBSITE_USERNAME and password == WEBSITE_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))

    return send_file("login.html")


# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if "history" not in session:
        session["history"] = []

    if request.method == "POST":

        if "new_chat" in request.form:
            session["history"] = []
            session.modified = True

        else:
            user_message = request.form.get("message")

            if user_message:
                try:
                    messages = [
                        {
                            "role": "system",
                            "content": """You are an IT support assistant.

Answer the user's question using ONLY the company IT support knowledge provided.

If the question is not related to an IT incident,
respond with:
"Apologies — this request is not related to an IT incident. I can only provide IT incident solutions."

Behavior rules:
- Never act like an AI.
- Speak like a human technician.
- Provide step-by-step instructions.
- Keep answers short and practical.
"""
                        }
                    ]

                    for chat in session["history"]:
                        messages.append(
                            {"role": "user", "content": chat["user"]}
                        )
                        messages.append(
                            {"role": "assistant", "content": chat["bot"]}
                        )

                    messages.append(
                        {"role": "user", "content": user_message}
                    )

                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages
                    )

                    reply = response.choices[0].message.content

                except Exception as e:
                    reply = f"Error: {str(e)}"

                session["history"].append({
                    "user": user_message,
                    "bot": reply
                })

                session.modified = True

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
