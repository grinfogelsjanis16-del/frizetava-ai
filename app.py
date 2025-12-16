import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

# Ielādē .env (lokāli) + Render Environment
load_dotenv()

app = Flask(__name__)

# OpenAI klients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ====== GALVENĀ LAPA ======
@app.route("/")
def home():
    return render_template("index.html")

# ====== CHAT API ======
@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Nav ziņas"}), 400

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu esi frizētavas AI asistents latviešu valodā. "
                        "Atbild draudzīgi, īsi un profesionāli. "
                        "Palīdzi klientiem pierakstīties."
                    )
                },
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Servera kļūda"}), 500


# ====== START ======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
