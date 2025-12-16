import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Vari pielāgot frizētavai
SALON_CONTEXT = """
Tu esi frizētavas virtuālais asistents latviešu valodā.
Mērķis: ātri, pieklājīgi un profesionāli atbildēt klientiem un palīdzēt pierakstīties.
Noteikumi:
- Ja trūkst informācijas (datums/laiks/pakalpojums), pajautā 1–2 precizējošus jautājumus.
- Piedāvā 2–3 laika alternatīvas, ja klients nav norādījis konkrētu laiku.
- Runā draudzīgi, bet bez liekas pļāpāšanas.
- Nekad neizdomā cenu, ja tā nav dota; ja nav cenu saraksta, saki: “cena atkarīga no… varu precizēt”.
"""

# Vienkāršs "cenu/pakalpojumu" piemērs (pielāgo sev)
SERVICES_INFO = """
Pakalpojumi (piemērs, vari nomainīt):
- Sieviešu griezums: 25–40€
- Vīriešu griezums: 15–25€
- Krāsošana: no 45€ (atkarīgs no garuma un tehnikas)
- Balayage: no 90€
- Fēns/ieveidošana: 20–35€
Adrese: (ieraksti savu)
Darba laiks: (ieraksti savu)
"""

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/reply")
def api_reply():
    data = request.get_json(force=True)
    user_message = (data.get("message") or "").strip()
    if not user_message:
        return jsonify({"error": "Tukša ziņa"}), 400

    # Lūdzam modelim atgriezt JSON (lai viegli parādīt UI)
    prompt = f"""
{SALON_CONTEXT}

Papildinformācija par salonu:
{SERVICES_INFO}

Klienta ziņa:
\"\"\"{user_message}\"\"\"

Atgriez TIKAI derīgu JSON (bez paskaidrojumiem), ar laukiem:
- reply: (teksts ko nosūtīt klientam)
- intent: (viena vērtība no: booking, price, info, reschedule, cancel, other)
- missing_info: (masīvs ar trūkstošajiem laukiem, piem. ["date","time","service"], vai [])
- suggested_next_question: (viens īss jautājums, ja vajag, citādi "")
"""

    resp = client.responses.create(
        model="gpt-5.2-mini",
        input=prompt
    )

    text = (resp.output_text or "").strip()

    # Droša JSON parsēšana (ar fallback)
    try:
        parsed = json.loads(text)
    except Exception:
        parsed = {
            "reply": text,
            "intent": "other",
            "missing_info": [],
            "suggested_next_question": ""
        }

    return jsonify(parsed)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


