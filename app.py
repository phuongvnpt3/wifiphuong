from flask import Flask, request, jsonify
import pandas as pd
import requests
import os

app = Flask(__name__)

# Cấu hình
OA_ACCESS_TOKEN = "7XXGTcL3LEjPNCiWNPOP"  # Thay bằng token thực của bạn
OA_SECRET_KEY = "RXK8PdDhGkfCiFbVQXgA"     # Thêm secret key của OA
ZALO_API_URL = "https://openapi.zalo.me/v3.0/oa/message"

# Load Excel
try:
    data_wifi = pd.read_excel("tu_khoa.xlsx", sheet_name="wifi")
    # Chuyển keyword sang chữ thường để so sánh dễ dàng
    tu_khoa['keyword'] = tu_khoa['keyword'].str.lower()
except Exception as e:
    print("Lỗi khi đọc file Excel:", str(e))
    tu_khoa = pd.DataFrame(columns=['keyword', 'response'])

def reply_to_user(user_id, message):
    headers = {
        "Content-Type": "application/json",
        "access_token": OA_ACCESS_TOKEN
    }
    payload = {
        "recipient": {
            "user_id": user_id
        },
        "message": {
            "text": message
        }
    }
    
    try:
        response = requests.post(ZALO_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        print("==> Đã gửi phản hồi thành công:", response.status_code)
        return True
    except requests.exceptions.RequestException as e:
        print("==> Lỗi khi gửi tin nhắn:", str(e))
        return False

@app.route("/", methods=["GET", "POST", "OPTIONS"])
def webhook():
    if request.method == "GET":
        # Xác thực webhook khi Zalo gửi yêu cầu GET
        oa_id = request.args.get("oaid")
        secret_key = request.args.get("secret_key")
        
        if oa_id == OA_ACCESS_TOKEN.split("_")[0] and secret_key == OA_SECRET_KEY:
            return jsonify({"status": "success"}), 200
        return jsonify({"status": "unauthorized"}), 403
    
    elif request.method == "OPTIONS":
        # Xử lý yêu cầu CORS OPTIONS
        return jsonify({"status": "success"}), 200
    
    elif request.method == "POST":
        try:
            data = request.get_json()
            print("==> Nhận dữ liệu từ Zalo:", data)

            # Kiểm tra sự kiện tin nhắn
            if data.get("event_name") == "user_send_text":
                user_id = data["sender"]["id"]
                user_msg = data["message"]["text"].strip().lower()
                print(f"==> Tin nhắn từ {user_id}: {user_msg}")

                # Tìm câu trả lời trong file Excel
                matched = tu_khoa[data_wifi['keyword'] == user_msg]
                
                if not matched.empty:
                    response = matched.iloc[0]['response']
                else:
                    response = "Xin lỗi, tôi không tìm thấy thông tin phù hợp. Vui lòng thử lại với từ khóa khác."

                # Gửi phản hồi
                reply_to_user(user_id, response)

            return jsonify({"status": "success"}), 200
        
        except Exception as e:
            print("==> Lỗi xử lý webhook:", str(e))
            return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Kiểm tra file Excel tồn tại
    if not os.path.exists("zalo_data.xlsx"):
        print("Cảnh báo: Không tìm thấy file zalo_data.xlsx")
    
    app.run(host="0.0.0.0", port=10000, debug=True)
