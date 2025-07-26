from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import requests
import os

app = Flask(__name__)

# ================= CẤU HÌNH ZALO OA =================
OA_ACCESS_TOKEN = "7XXGTcL3LEjPNCiWNPOP"
OA_SECRET_KEY = "RXK8PdDhGkfCiFbVQXgA"
ZALO_API_URL = "https://openapi.zalo.me/v3.0/oa/message"
# =====================================================

try:
    # Đọc file Excel với từ khóa
    keyword_data = pd.read_excel("tu_khoa.xlsx", sheet_name=0)
    
    # Chuẩn hóa keyword: chữ thường và bỏ khoảng trắng thừa
    keyword_data['keyword'] = keyword_data['keyword'].str.strip().str.lower()
    
    print("✅ Đã tải dữ liệu từ khóa thành công")
    print(keyword_data)
except Exception as e:
    print(f"❌ Lỗi khi đọc file Excel: {str(e)}")
    keyword_data = pd.DataFrame(columns=['keyword', 'response'])

def reply_to_user(user_id, message):
    """Gửi tin nhắn phản hồi đến người dùng qua Zalo API"""
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
        print(f"✅ Đã gửi phản hồi cho {user_id}: {message}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi khi gửi tin nhắn: {str(e)}")
        print(f"URL: {ZALO_API_URL}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        return False

# Route xác thực webhook bằng file HTML
@app.route("/zalo_verifierSlgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html")
def zalo_verifier():
    return send_from_directory('.', 'zalo_verifierSlgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html')

# Webhook chính
@app.route("/", methods=["GET", "POST", "OPTIONS"])
def webhook():
    # Xử lý yêu cầu xác thực webhook (GET)
    if request.method == "GET":
        oa_id = request.args.get("oaid")
        secret_key = request.args.get("secret_key")
        
        if oa_id and secret_key:
            # Kiểm tra thông tin xác thực
            if secret_key == OA_SECRET_KEY:
                print("✅ Xác thực webhook thành công (Secret Key đúng)")
                return jsonify({"status": "success"}), 200
            else:
                print("❌ Xác thực webhook thất bại: Secret Key không khớp")
                return jsonify({"status": "unauthorized"}), 403
        return "Zalo OA Webhook", 200

    # Xử lý yêu cầu OPTIONS (CORS)
    elif request.method == "OPTIONS":
        return jsonify({"status": "success"}), 200

    # Xử lý sự kiện từ Zalo (POST)
    elif request.method == "POST":
        try:
            data = request.get_json()
            print("📨 Dữ liệu nhận được:", data)

            # Kiểm tra tính hợp lệ của dữ liệu
            if not data or "event_name" not in data:
                print("⚠️ Dữ liệu không hợp lệ từ Zalo")
                return jsonify({"status": "invalid_data"}), 400

            # Chỉ xử lý sự kiện người dùng gửi tin nhắn văn bản
            if data.get("event_name") == "user_send_text":
                user_id = data["sender"]["id"]
                user_message = data["message"]["text"].strip().lower()
                print(f"👤 {user_id}: {user_message}")

                # Tìm phản hồi phù hợp trong dữ liệu
                matched = keyword_data[keyword_data['keyword'] == user_message]
                
                if not matched.empty:
                    response_text = matched.iloc[0]['response']
                else:
                    # Tạo danh sách từ khóa gợi ý
                    suggestions = ", ".join(keyword_data['keyword'].tolist())
                    response_text = (
                        "Xin lỗi, tôi không hiểu câu hỏi của bạn.\n\n"
                        "Vui lòng thử một trong các từ khóa sau:\n"
                        f"{suggestions}"
                    )

                # Gửi phản hồi
                reply_to_user(user_id, response_text)

            return jsonify({"status": "success"}), 200
        
        except Exception as e:
            print(f"🔥 Lỗi nghiêm trọng: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Kiểm tra các file cần thiết
    required_files = [
        "tu_khoa.xlsx",
        "zalo_verifierSlgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"⚠️ Cảnh báo: Thiếu các file quan trọng: {', '.join(missing_files)}")
    else:
        print("✅ Tất cả file cần thiết đã sẵn sàng")
    
    print("🚀 Khởi chạy chatbot Zalo OA...")
    print(f"👉 Access Token: {OA_ACCESS_TOKEN}")
    print(f"👉 Secret Key: {OA_SECRET_KEY}")
    print(f"👉 Webhook URL: http://0.0.0.0:10000/")
    app.run(host="0.0.0.0", port=10000, debug=True)