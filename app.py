
from flask import Flask, request, jsonify, send_from_directory
import pandas as pd

app = Flask(__name__)

# Tải dữ liệu từ Excel
df = pd.read_excel("data.xlsx")  # Đảm bảo file này nằm cùng thư mục với app.py

# Đọc file Excel thành từ điển từ khóa và phản hồi
response_dict = dict(zip(df["Từ khóa"], df["Trả lời"]))

@app.route('/', methods=['GET'])
def home():
    return 'Chatbot Zalo đang hoạt động!'

@app.route('/zalo_verifierSIgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html', methods=['GET'])
def verify_domain():
    return send_from_directory('.', 'zalo_verifierSIgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        user_id = data['sender']['id']
        message = data['message']['text']

        response = None
        for keyword in response_dict:
            if keyword.lower() in message.lower():
                response = response_dict[keyword]
                break

        if response:
            print(f"Gửi phản hồi tới {user_id}: {response}")
        else:
            print(f"Không tìm thấy phản hồi cho: {message}")

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Lỗi webhook:", e)
        return jsonify({"status": "error"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
