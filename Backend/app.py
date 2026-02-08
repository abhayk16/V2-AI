from flask import Flask, request, send_file
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Home route
@app.route("/", methods=["GET", "POST"])
def home():
    reply = ""

    if request.method == "POST":
        user_message = request.form.get("message")

        if user_message:
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_message}
                    ]
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"Error: {str(e)}"

    # Always load and replace
    with open("../Frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{reply}}", reply)
    return html


    return send_file("../Frontend/index.html")


# Serve CSS
@app.route("/style.css")
def style():
    return send_file("../Frontend/style.css")



if __name__ == "__main__":
    app.run(debug=True)
