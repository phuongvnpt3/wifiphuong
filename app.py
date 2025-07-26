from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import requests
import os
import logging
import time

app = Flask(__name__)

# Cấu hình logging chi tiết
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('zalo-chatbot')

# ================= CẤU HÌNH ZALO OA =================
OA_ACCESS_TOKEN = "cxb2DamE246OlaurIWW5GfkwG39C46eZmwDn0q1KQGhdddqJIqL089kv03Oi3Kic_zWE470e71occmm7CMaJ9OMlE2ufHte3-P4_4cXF3GN2faOpPsr5CigEGK9QVL5MaRiFN3bqCcwUmnHzInPKRU6WSXO_PLWAZefR4o1iSXUPW7CaI4b2K_kI2NXNVJ5eo9u6P1z94qoBh0uyNKOPIUs9HsL2MG1LoxSxHqLVV66QipjdE4GgS8coAtiQUmT9X94IQ3TNAs6zfWj7C7KfIg-mOc8BLtLoZx5JGoPbKr6MWrb8HLGVFSIu2GXdP10CwwDHVrT4H6Fsedj1M7bZUzseHqb_TNmyxQ9W2L8N93d1um8TU0C7P_l_ENvH73nRzj8XKNKp5271zHuuH0ahITF9Q4LoDUQ4SqD94m13"
OA_SECRET_KEY = "RXK8PdDhGkfCiFbVQXgA"
ZALO_API_URL = "https://openapi.zalo.me/v3.0/oa/message"
# =====================================================

# Đọc dữ liệu từ khóa
keyword_data = pd.DataFrame(columns=['keyword', 'response'])
try:
    if os.path.exists("tu_khoa.xlsx"):
        # Đọc file Excel với từ khóa
        keyword_data = pd.read_excel("tu_khoa.xlsx", sheet_name=0)
        
        # Chuẩn hóa keyword: chữ thường và bỏ khoảng trắng thừa
        keyword_data['keyword'] = keyword_data['keyword'].str.strip().str.lower()
        
        logger.info("✅ Đã tải dữ liệu từ khóa thành công")
        logger.info(f"Số lượng từ khóa: {len(keyword_data)}")
    else:
        logger.error("❌ File 'tu_khoa.xlsx' không tồn tại")
except Exception as e:
    logger.error(f"❌ Lỗi khi đọc file Excel: {str(e)}")

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
        start_time = time.time()
        response = requests.post(ZALO_API_URL, headers=headers, json=payload, timeout=10)
        elapsed = (time.time() - start_time) * 1000
        
        # Ghi log chi tiết
        logger.info(f"🔔 Phản hồi từ Zalo API [{response.status_code}] trong {elapsed:.2f}ms")
        
        if response.status_code == 200:
            logger.info(f"✅ Đã gửi phản hồi thành công cho {user_id}")
            return True
        else:
            # Phân tích lỗi chi tiết từ Zalo
            try:
                error_data = response.json()
                error_code = error_data.get('error', -1)
                error_msg = error_data.get('message', 'Unknown error')
                
                logger.error(f"❌ Lỗi Zalo API [{error_code}]: {error_msg}")
                
                # Xử lý các lỗi phổ biến
                if error_code == 124:  # Token không hợp lệ
                    logger.critical("⚠️ TOKEN KHÔNG HỢP LỆ! Vui lòng kiểm tra lại Access Token")
                elif error_code == 10:  # Quá tải request
                    logger.warning("⚠️ Quá tải request, thử lại sau")
                
            except:
                logger.error(f"❌ Không thể phân tích phản hồi lỗi: {response.text}")
            
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Lỗi kết nối khi gửi tin nhắn: {str(e)}")
        return False

# Route xác thực webhook bằng file HTML
@app.route("/zalo_verifierSlgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html")
def zalo_verifier():
    logger.info("✅ Phục vụ file xác thực Zalo")
    return send_from_directory('.', 'zalo_verifierSlgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html')

# Webhook chính - SỬA LỖI THIẾU XỬ LÝ HEAD
@app.route("/", methods=["GET", "POST", "OPTIONS", "HEAD"])
def webhook():
    # Xử lý yêu cầu HEAD (Health Check)
    if request.method == "HEAD":
        logger.info("🔄 Xử lý yêu cầu HEAD (Health Check)")
        return "", 200

    # Xử lý yêu cầu xác thực webhook (GET)
    if request.method == "GET":
        oa_id = request.args.get("oaid")
        secret_key = request.args.get("secret_key")
        
        logger.info(f"🔍 Yêu cầu GET từ Zalo: oaid={oa_id}, secret_key={secret_key}")
        
        if oa_id and secret_key:
            # Kiểm tra thông tin xác thực
            if secret_key == OA_SECRET_KEY:
                logger.info("✅ Xác thực webhook thành công (Secret Key đúng)")
                return jsonify({"status": "success"}), 200
            else:
                logger.warning("❌ Xác thực webhook thất bại: Secret Key không khớp")
                return jsonify({"status": "unauthorized"}), 403
        return "Zalo OA Webhook", 200

    # Xử lý yêu cầu OPTIONS (CORS)
    elif request.method == "OPTIONS":
        logger.info("🔄 Xử lý yêu cầu OPTIONS (CORS)")
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return jsonify({"status": "success"}), 200, headers

    # Xử lý sự kiện từ Zalo (POST)
    elif request.method == "POST":
        try:
            # Ghi log dữ liệu thô nhận được
            raw_data = request.data.decode('utf-8')
            logger.info(f"📨 Nhận yêu cầu POST từ Zalo")
            
            data = request.get_json()
            if not data:
                logger.error("⚠️ Không có dữ liệu JSON trong yêu cầu POST")
                return jsonify({"status": "invalid_data"}), 400
                
            event_name = data.get("event_name")
            logger.info(f"ℹ️ Sự kiện nhận được: {event_name}")

            # Xử lý tin nhắn văn bản
            if event_name == "user_send_text":
                # Kiểm tra cấu trúc dữ liệu
                if "sender" not in data or "id" not in data["sender"]:
                    logger.error("❌ Thiếu thông tin người gửi")
                    return jsonify({"status": "invalid_sender"}), 400
                    
                if "message" not in data or "text" not in data["message"]:
                    logger.error("❌ Thiếu nội dung tin nhắn")
                    return jsonify({"status": "invalid_message"}), 400
                
                user_id = data["sender"]["id"]
                user_message = data["message"]["text"].strip().lower()
                logger.info(f"👤 Tin nhắn từ {user_id}: '{user_message}'")

                # Tìm phản hồi phù hợp trong dữ liệu
                matched = keyword_data[keyword_data['keyword'] == user_message]
                
                if not matched.empty:
                    response_text = matched.iloc[0]['response']
                    logger.info(f"🔍 Tìm thấy phản hồi cho '{user_message}'")
                else:
                    # Tạo danh sách từ khóa gợi ý
                    suggestions = ", ".join(keyword_data['keyword'].tolist())
                    response_text = (
                        "Xin lỗi, tôi không hiểu câu hỏi của bạn.\n\n"
                        "Vui lòng thử một trong các từ khóa sau:\n"
                        f"{suggestions}"
                    )
                    logger.warning(f"⚠️ Không tìm thấy từ khóa '{user_message}'")

                # Gửi phản hồi
                logger.info(f"✉️ Chuẩn bị gửi phản hồi cho {user_id}")
                if reply_to_user(user_id, response_text):
                    logger.info(f"✅ Đã gửi phản hồi thành công cho {user_id}")
                else:
                    logger.error(f"❌ Gửi phản hồi thất bại cho {user_id}")
            else:
                logger.info(f"⏩ Bỏ qua sự kiện: {event_name}")

            return jsonify({"status": "success"}), 200
        
        except Exception as e:
            logger.error(f"🔥 LỖI NGHIÊM TRỌNG: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500

    # Xử lý các phương thức khác
    return jsonify({"status": "method_not_allowed"}), 405

if __name__ == "__main__":
    # Kiểm tra các file cần thiết
    required_files = [
        "tu_khoa.xlsx",
        "zalo_verifierSlgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        logger.warning(f"⚠️ CẢNH BÁO: Thiếu file: {', '.join(missing_files)}")
    else:
        logger.info("✅ Tất cả file cần thiết đã sẵn sàng")
    
    logger.info("🚀 KHỞI CHẠY CHATBOT ZALO OA")
    logger.info(f"🔑 Access Token: {OA_ACCESS_TOKEN}")
    logger.info(f"🔒 Secret Key: {OA_SECRET_KEY}")
    logger.info(f"🌐 Webhook URL: http://0.0.0.0:10000/")
    
    # Kiểm tra kết nối đến Zalo API
    try:
        logger.info("🔍 Kiểm tra kết nối đến Zalo API...")
        test_response = requests.get("https://openapi.zalo.me", timeout=5)
        if test_response.status_code == 200:
            logger.info("✅ Kết nối thành công đến Zalo API")
        else:
            logger.warning(f"⚠️ Cảnh báo: Kết nối Zalo API trả về mã {test_response.status_code}")
    except Exception as e:
        logger.error(f"❌ Lỗi kết nối đến Zalo API: {str(e)}")
    
    # Kiểm tra dữ liệu từ khóa
    if len(keyword_data) > 0:
        logger.info(f"📊 Tải thành công {len(keyword_data)} từ khóa")
    else:
        logger.critical("❌ KHÔNG CÓ DỮ LIỆU TỪ KHÓA NÀO ĐƯỢC TẢI")
    
    # Sử dụng PORT từ biến môi trường cho Render.com
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port, debug=False)