import streamlit as st
import random
import math
from supabase import create_client, Client

# --- Supabase の設定 ---
# 環境変数から取得することを推奨します。
# secrets.toml を使う場合は st.secrets を使います。
url: str = "https://pszefvosagdpzilocerq.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBzemVmdm9zYWdkcHppbG9jZXJxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4ODU1NTIsImV4cCI6MjA2MDQ2MTU1Mn0.nRw_Ev8VGVf_PvnQZ5Lk10JPYg3jaJwUWkGCmNO03fA"

supabase: Client = create_client(url, key)

# --- パチンコシミュレーション関数群（変更なし） ---
def lot_norm(hatuatari):
    attempts = 0
    WINNING_NUMBER = 1
    while True:
        attempts += 1
        drawn_number = random.randint(1, hatuatari)
        if drawn_number == WINNING_NUMBER:
            break
    return attempts

def inves_money(hatuatari, kaitensu):
    hit_num = lot_norm(hatuatari)
    number = hit_num / kaitensu * 1000
    divided_and_ceiled = math.ceil(number / 500)
    return hit_num, int(divided_and_ceiled * 500)

def lot_special(hatuatari, densapo):
    attempts = 0
    hit_attemps = 0
    special_attemps = 0
    scoles = 0
    WINNING_NUMBER = 1
    while True:
        attempts += 1
        drawn_number = random.randint(1, hatuatari)
        if drawn_number == WINNING_NUMBER:
            drawn_number2 = random.randint(1, 100)
            if drawn_number2 < 4:
                scoles += 6000
                special_attemps += 1
                attempts = 0
            else:
                scoles += 3000
                hit_attemps += 1
                attempts = 0
        else:
            if attempts == densapo:
                break
    return hit_attemps, special_attemps, scoles

# --- Streamlit アプリケーションのUIとロジック ---
st.set_page_config(page_title="パチンコシミュレーター", layout="centered")
st.title("🎰 パチンコシミュレーション")

st.write("ボタンを押すと1回分のパチンコシミュレーションを実行し、結果を表示します。")
st.write("シミュレーション結果はSupabaseデータベースに記録されます。")

# ユーザーが設定できるパラメータ
st.sidebar.header("シミュレーション設定")
initial_prob = st.sidebar.slider("初当たり確率 (1/)", 10, 500, 199, step=1)
revolutions_per_1000yen = st.sidebar.slider("1000円あたりの回転数", 10, 30, 18, step=1)
rush_prob = st.sidebar.slider("ラッシュ中確率 (1/)", 10, 200, 95, step=1)
densapo_count = st.sidebar.slider("電サポ回数", 50, 200, 130, step=5)


if st.button("シミュレーションを実行！"):
    # シミュレーションの実行
    hit_num, hit_inves = inves_money(initial_prob, revolutions_per_1000yen)
    total_scoles = 0
    result_type = ""
    rush_info = {}

    lot_mode = random.randint(1, 100)
    if lot_mode <= 50: # 50%でチャージ
        total_scoles = 1200 - hit_inves
        result_type = "チャージ"
    else: # 50%でラッシュ分岐
        lot_charge = random.randint(1, 2)
        if lot_charge == 1: # 1/2で単発
            total_scoles = 6000 - hit_inves
            result_type = "単発"
        else: # ラッシュ突入
            rush_num, special_num, rush_raw_score = lot_special(rush_prob, densapo_count)
            # 出玉を円に換算（例: 1玉4円と仮定）
            # もし rush_raw_score が玉数ではなく点数なら、適切な換算が必要です。
            # 元のコードの 4*rush_resrt-hit_inves は、rush_resrt が玉数で、1玉4円という計算式に見えます。
            # 今回の scoles は「点数」で 3000/6000 なので、換算のロジックを合わせる必要があります。
            # 仮に3000点 = 1500玉, 6000点 = 3000玉 とし、1玉4円で計算します。
            # 1500玉 * 4円 = 6000円
            # 3000玉 * 4円 = 12000円
            # つまり、raw_score をそのまま円として扱う方が元のロジックに近いかもしれません。
            # あるいは、点数を玉数に変換するロジックが必要です。
            # ここでは、元のコードの scoles += 1500 が 1500発、scoles += 3000 が 3000発の誤記だと仮定して、
            # scoles を「得点」ではなく「出玉」として計算されたものと解釈し、単純に4をかけます。
            # もし scoles が「点数」であり、1点あたりの価値がある場合は、ここを調整してください。
            total_scoles = (rush_raw_score * 4) - hit_inves
            result_type = "ラッシュ"
            rush_info = {
                "rush_count": rush_num,
                "special_rush_count": special_num,
                "raw_rush_score": rush_raw_score # 点数または玉数
            }

    # Supabase へのデータ挿入
    try:
        data_to_insert = {
            "hit_count": hit_num,
            "result_type": result_type,
            "total_score": total_scoles,
            "initial_investment": hit_inves # 投資額も保存
        }
        if result_type == "ラッシュ":
            data_to_insert["rush_count"] = rush_info["rush_count"]
            data_to_insert["special_rush_count"] = rush_info["special_rush_count"]
            # raw_rush_score は Supabase に直接保存しないかもしれません
            # data_to_insert["raw_rush_score"] = rush_info["raw_rush_score"]

        response = supabase.table("ghole").insert(data_to_insert).execute()
        # st.success("結果をSupabaseに保存しました！") # デバッグ用
        # print(response) # デバッグ用
    except Exception as e:
        st.error(f"Supabaseへの保存中にエラーが発生しました: {e}")

    # 結果の表示
    st.subheader("--- シミュレーション結果 ---")
    st.write(f"**初当たりまでの回転数**: {hit_num}回")
    st.write(f"**初期投資額**: {hit_inves}円")
    st.write(f"**結果タイプ**: {result_type}")
    st.write(f"**最終収支**: {total_scoles}円")

    if result_type == "ラッシュ":
        st.write(f"  - **ラッシュ回数**: {rush_info['rush_count']}回")
        st.write(f"  - **6000発ラッシュ回数**: {rush_info['special_rush_count']}回")
        # st.write(f"  - ラッシュ中獲得点数/玉数: {rush_info['raw_rush_score']}") # 必要であれば表示

    st.info("別のシミュレーションを実行するには、再度ボタンを押してください。")