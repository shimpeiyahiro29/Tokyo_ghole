import random
import math
from supabase import create_client, Client
from flask import Flask, request, jsonify
from flask_cors import CORS # For handling Cross-Origin Resource Sharing

# Supabase Credentials (from your original code)
# Note: For production, it's recommended to use environment variables for keys.
SUPABASE_URL: str = "https://pszefvosagdpzilocerq.supabase.co"
SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBzemVmdm9zYWdkcHppbG9jZXJxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4ODU1NTIsImV4cCI6MjA2MDQ2MTU1Mn0.nRw_Ev8VGVf_PvnQZ5Lk10JPYg3jaJwUWkGCmNO03fA"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for all routes, allowing your HTML frontend to make requests
CORS(app)

# --- パチンコシミュレーション関数群 (変更なし) ---
def lot_norm(hatuatari: int) -> int:
    """
    初当たりまでの回転数をシミュレーションします。
    :param hatuatari: 初当たりの確率分母 (例: 319)
    :return: 初当たりまでの回転数
    """
    attempts = 0
    WINNING_NUMBER = 1 # 1を引くと当たり
    while True:
        attempts += 1
        drawn_number = random.randint(1, hatuatari)
        if drawn_number == WINNING_NUMBER:
            break
    return attempts

def inves_money(hatuatari: int, kaitensu: int) -> tuple[int, int]:
    """
    初当たりまでの回転数と投資額を計算します。
    :param hatuatari: 初当たりの確率分母
    :param kaitensu: 1000円あたりの回転数
    :return: (初当たりまでの回転数, 投資額)
    """
    hit_num = lot_norm(hatuatari)
    # 投資額を計算 (回転数から千円あたりの投資額を算出)
    # hit_num回転回すのに必要な千円単位の投資額 = (hit_num / kaitensu)
    # これに1000を掛けて円単位に変換
    investment_needed = (hit_num / kaitensu) * 1000
    # 500円単位に切り上げ
    rounded_investment = math.ceil(investment_needed / 500) * 500
    return hit_num, int(rounded_investment)

def lot_special(hatuatari: int, densapo: int) -> tuple[int, int, int]:
    """
    ラッシュ中の大当りシミュレーションと獲得スコアを計算します。
    :param hatuatari: ラッシュ中の大当り確率分母 (例: 99)
    :param densapo: 電サポ回数 (例: 163)
    :return: (当選回数, 特別当選回数, 獲得スコア)
    """
    attempts = 0
    special_attemps = 0 # 特別当選（大当り）回数
    scoles = 0 # 獲得スコア (玉数など)
    WINNING_NUMBER = 1 # 1を引くと当たり

    while True:
        attempts += 1
        drawn_number = random.randint(1, hatuatari)
        if drawn_number == WINNING_NUMBER:
            scoles += 1500 # 大当り1回あたりの獲得スコア (例: 1500玉)
            special_attemps += 1
            attempts = 0 # 大当りすると電サポ回数がリセットされると仮定
        else:
            if attempts == densapo:
                break # 電サポ回数を超えたら終了
    return 0, special_attemps, scoles # hit_attemps はこの関数では使用しないので0

# --- Flask API エンドポイント ---
@app.route('/simulate', methods=['POST'])
def simulate():
    """
    パチンコシミュレーションを実行し、結果を返すAPIエンドポイント。
    フロントエンドから投資額あたりの回転数を受け取り、シミュレーションを実行します。
    """
    data = request.get_json()
    revolutions_per_1000yen = data.get('revolutions_per_1000yen', 18) # デフォルト値18

    try:
        # シミュレーションの実行
        hit_num, hit_inves = inves_money(319, revolutions_per_1000yen)
        total_scoles = 0
        result_type = ""
        rush_info = {}

        lot_mode = random.randint(1, 100)
        if lot_mode <= 50: # 50%で単発または引き戻し
            # このブロックは、元々のStreamlitコードのロジックを忠実に再現
            chance_num, chance_inves = inves_money(319, revolutions_per_1000yen)
            if chance_num < 100:
                # 引き戻し (RUSH突入)
                rush_hit_count, special_rush_num, rush_raw_score = lot_special(99, 163)
                total_scoles = (rush_raw_score * 4) + 7800 - hit_inves - chance_inves
                result_type = "引き戻し"
                rush_info = {
                    "rush_count": special_rush_num,
                    "raw_rush_score": rush_raw_score
                }
            else:
                # 単発
                total_scoles = 1800 - hit_inves
                result_type = "単発"
        else: # 50%でラッシュ分岐 (RUSH直撃)
            rush_hit_count, special_rush_num, rush_raw_score = lot_special(99, 163)
            total_scoles = (rush_raw_score * 4) + 1800 - hit_inves
            result_type = "ラッシュ"
            rush_info = {
                "rush_count": special_rush_num,
                "raw_rush_score": rush_raw_score
            }

        # Supabase へのデータ挿入
        data_to_insert = {
            "hit_count": hit_num,
            "result_type": result_type,
            "total_score": total_scoles,
            "initial_investment": hit_inves
        }
        if result_type in ["ラッシュ", "引き戻し"]:
            data_to_insert["rush_count"] = rush_info["rush_count"]
            # data_to_insert["raw_rush_score"] = rush_info["raw_rush_score"] # 元コードでコメントアウトされていたのでここでもコメントアウト

        response = supabase.table("eva").insert(data_to_insert).execute()
        # print("Supabase Response:", response) # デバッグ用

        # 結果をJSONとして返す
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
        return jsonify({"success": False, "error": str(e)}), 500

# This block allows you to run the Flask app directly
if __name__ == '__main__':
    app.run(debug=True, port=5000) # デバッグモードでポート5000で実行
