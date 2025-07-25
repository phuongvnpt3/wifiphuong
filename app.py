import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

def load_keywords():
    df = pd.read_excel("tu_khoa.xlsx", engine='openpyxl')
    df.columns = ["keyword", "answer"]
    return dict(zip(df["keyword"].str.lower(), df["answer"]))

keywords = load_keywords()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return jsonify({"status": "ok"})
    return "Server is ready"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or 'data' not in data:
        return jsonify({"status": "invalid"}), 400
    user_id = data['data']['user_id']
    message = data['data']['message'].lower()
    reply = "Xin lỗi, mình chưa hiểu yêu cầu."

    for kw, ans in keywords.items():
        if kw in message:
            reply = ans
            break

    requests.post("https://openapi.zalo.me/v2.0/oa/message",
                  headers={
                    "access_token": os.getenv("ZALO_OA_ACCESS_TOKEN"),
                    "Content-Type": "application/json"
                  },
                  json={"recipient": {"user_id": user_id}, "message": {"text": reply}})
    return jsonify({"status": "ok"}), 200
