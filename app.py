from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load từ khóa từ file Excel
def load_keywords():
    df = pd.read_excel("tu_khoa.xlsx")
    df.columns = ["keyword", "answer"]
    return dict(zip(df["keyword"], df["answer"]))

keywords = load_keywords()

@app.route("/", methods=["GET"])
def index():
    return "Zalo OA Chatbot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        user_id = data['data']['user_id']
        message = data['data']['message']

        # Xử lý tìm từ khóa phù hợp
        response = "Xin lỗi, tôi chưa hiểu yêu cầu."
        for keyword in keywords:
            if keyword.lower() in message.lower():
                response = keywords[keyword]
                break

        print(f"Tin nhắn từ {user_id}: {message}")
        print(f"Trả lời: {response}")

        return jsonify({"status": "ok", "reply": response})
    except Exception as e:
        print("Lỗi:", e)
        return jsonify({"status": "error", "detail": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)