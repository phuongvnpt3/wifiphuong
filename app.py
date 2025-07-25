from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/')
def home():
    return 'Zalo Verify Server is Running!'

@app.route('/zalo_verifierSlgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html')
def verify():
    return send_from_directory('.', 'zalo_verifierSlgK3gJy7Gf4pCmNcE5vEagNeoMcuNHwCJ0q.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
