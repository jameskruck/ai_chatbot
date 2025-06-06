from flask import Flask, request, jsonify
import openai
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

conversation_histories = {}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "default")
    user_message = data.get("message", "")

    if user_id not in conversation_histories:
        conversation_histories[user_id] = [{"role": "system", "content": "You are a helpful AI assistant."}]

    conversation_histories[user_id].append({"role": "user", "content": user_message})

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_histories[user_id],
            temperature=0.7
        )

        ai_response = response.choices[0].message.content
        conversation_histories[user_id].append({"role": "assistant", "content": ai_response})

        return jsonify({"response": ai_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))