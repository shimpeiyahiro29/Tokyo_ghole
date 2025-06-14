import os
from flask import Flask, jsonify
from flask_cors import CORS

# Flaskアプリのインスタンスを作成
app = Flask(__name__)

# CORSを有効にする (フロントエンドからのアクセスを許可)
CORS(app)

# シンプルなルートを作成
@app.route('/')
def home():
    return jsonify({"message": "Hello from my Flask app on Render!"})

# これまでの 'app.run()' の部分は完全に削除してください。
# Gunicornがサーバーの起動を管理します。