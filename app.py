import random
import math
from supabase import create_client, Client
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Supabase Credentials (環境変数から読み込むように変更)
# デプロイ時にSUPABASE_URLとSUPABASE_KEYの環境変数をRenderに設定していることを確認してください。
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://pszefvosagdpzilocerq.supabase.co")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBzemVmdm9zYWdkcHppbG9jZXJxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4ODU1NTIsImV4cCI6MjA2MDQ2MTU1Mn0.nRw_Ev8VGVf_PvnQZ5Lk10JPYg3jaJwUWkGCmNO03fA")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for all routes, allowing your HTML frontend to make requests
CORS(app)

# --- パチンコシミュレーション関数群 (変更なし) ---
def lot_norm(hatuatari: int) -> int:
    attempts = 0
    WINNING_NUMBER = 1
    while True:
        attempts += 1
        drawn_number = random.randint(1, hatuatari)
        if drawn_number == WINNING_NUMBER:
            break
    return attempts

def inves_money(hatuatari: int, kaitensu: int) -> tuple[int, int]:
    hit_num = lot_norm(hatuatari)
    investment_needed = (hit_num / kaitensu) * 1000
    rounded_investment = math.ceil(investment_needed / 500) * 500
    return hit_num, int(rounded_investment)

def lot_special(hatuatari: int, densapo: int) -> tuple[int, int, int]:
    attempts = 0
    special_attemps = 0
    scoles = 0
    WINNING_NUMBER = 1
    while True:
        attempts += 1
        drawn_number = random.randint(1, hatuatari)
        if drawn_number == WINNING_NUMBER:
            scoles += 1500
            special_attemps += 1
            attempts = 0
        else:
            if attempts == densapo:
                break
    return 0, special_attemps, scoles

# --- Flask API エンドポイント ---
@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    revolutions_per_1000yen = data.get('revolutions_per_1000yen', 18)

    try:
        hit_num, hit_inves = inves_money(319, revolutions_per_1000yen)
        total_scoles = 0
        result_type = ""
        rush_info = {}

        lot_mode = random.randint(1, 100)
        if lot_mode <= 50:
            chance_num, chance_inves = inves_money(319, revolutions_per_1000yen)
            if chance_num < 100:
                rush_hit_count, special_rush_num, rush_raw_score = lot_special(99, 163)
                total_scoles = (rush_raw_score * 4) + 7800 - hit_inves - chance_inves
                result_type = "引き戻し"
                rush_info = {
                    "rush_count": special_rush_num,
                    "raw_rush_score": rush_raw_score
                }
            else:
                total_scoles = 1800 - hit_inves
                result_type = "単発"
        else:
            rush_hit_count, special_rush_num, rush_raw_score = lot_special(99, 163)
            total_scoles = (rush_raw_score * 4) + 1800 - hit_inves
            result_type = "ラッシュ"
            rush_info = {
                "rush_count": special_rush_num,
                "raw_rush_score": rush_raw_score
            }

        data_to_insert = {
            "hit_count": hit_num,
            "result_type": result_type,
            "total_score": total_scoles,
            "initial_investment": hit_inves
        }
        if result_type in ["ラッシュ", "引き戻し"]:
            data_to_insert["rush_count"] = rush_info["rush_count"]

        response = supabase.table("eva").insert(data_to_insert).execute()

        return jsonify({
            "success": True,
            "hit_num": hit_num,
            "initial_investment": hit_inves,
            "result_type": result_type,
            "total_score": total_scoles,
            "rush_info": rush_info if rush_info else None
        })

    except Exception as e:
        print(f"シミュレーション中にエラーが発生しました: {e}")
        # エラーメッセージをログに出力し、フロントエンドにも返す
        return jsonify({"success": False, "error": str(e)}), 500

# Gunicornを使用する場合、このifブロックは実行されません。
# Gunicornが直接 'app:app' を読み込むため、削除しても問題ありません。
# 残していても動作には影響ありませんが、混乱を避けるために削除しても良いでしょう。
# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)