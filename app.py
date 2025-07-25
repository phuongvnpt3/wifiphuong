from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# === Tải từ khóa và trả lời từ file Excel ===
def load_keywords():
    df = pd.read_excel("tu_khoa.xlsx")
    df.columns = ["keyword", "answer"]
    return dict(zip(df["keyword"], df["answer"]))

keywords = load_keywords()

# === Route xác minh webhook của Zalo (GET hoặc POST) ===
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return "Zalo OA Chatbot is running with webhook verification!"
    elif request.method == "POST":
        return jsonify({"status": "ok"})  # Để Zalo xác thực webhook

# === Trả file xác minh (nếu cần đặt file .html để xác thực Zalo) ===
@app.route('/zalo_verifierSlgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html')
def verify():
    return send_from_directory('.', 'zalo_verifierSlgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html')

# === Webhook xử lý tin nhắn người dùng ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        user_id = data['data']['user_id']
        message = data['data']['message']

        # Trả lời mặc định
        response = "Xin lỗi, tôi chưa hiểu yêu cầu."

        # Tìm từ khóa phù hợp
        for keyword in keywords:
            if keyword.lower() in message.lower():
                response = keywords[keyword]
                break

        print(f"Tin nhắn từ {user_id}: {message}")
        print(f"Trả lời: {response}")

        return jsonify({"status": "ok", "reply": response})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 400

# === Chạy ứng dụng Flask ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)