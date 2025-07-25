from flask import Flask, request
import pandas as pd
import requests

app = Flask(__name__)

OA_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
ZALO_API_URL = "https://openapi.zalo.me/v3.0/oa/message"

# Load Excel
data_wifi = pd.read_excel("zalo_data.xlsx", sheet_name="wifi")

def reply_to_user(user_id, message):
    headers = {
        "Content-Type": "application/json",
        "access_token": OA_ACCESS_TOKEN
    }
    payload = {
        "recipient": {"user_id": user_id},
        "message": {"text": message}
    }
    response = requests.post(ZALO_API_URL, headers=headers, json=payload)
    print("==> Đã gửi phản hồi:", response.status_code, response.text)

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("==> Nhận JSON từ Zalo:", data)

        if data.get("event_name") == "user_send_text":
            user_id = data["sender"]["id"]
            user_msg = data["message"]["text"].strip().lower()
            print(f"==> Tin nhắn từ {user_id}: {user_msg}")

            matched = data_wifi[data_wifi['keyword'].str.lower() == user_msg]

            if not matched.empty:
                response = matched.iloc[0]['response']
            else:
                response = "Xin lỗi, tôi chưa hiểu câu hỏi của bạn."

            reply_to_user(user_id, response)

        return "OK", 200
    except Exception as e:
        print("==> Lỗi xử lý webhook:", str(e))
        return "Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
