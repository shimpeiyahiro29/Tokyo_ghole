import streamlit as st
import random
import math
from supabase import create_client, Client

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
            scoles += 1500
            special_attemps += 1
            attempts = 0
        else:
            if attempts == densapo:
                break
    return hit_attemps, special_attemps, scoles

# --- Streamlit アプリケーションのUIとロジック ---
st.set_page_config(page_title="パチンコシミュレーター eva", layout="centered")
st.title("🎰 未来への咆哮")

st.write("ボタンを押すと1回分のパチンコシミュレーションを実行し、結果を表示します。")
st.write("シミュレーション結果はSupabaseデータベースに記録されます。")

# ユーザーが設定できるパラメータ
st.sidebar.header("シミュレーション設定")
revolutions_per_1000yen = st.sidebar.slider("1000円あたりの回転数", 10, 30, 18, step=1)


if st.button("シミュレーションを実行！"):
    # シミュレーションの実行
    hit_num, hit_inves = inves_money(319, revolutions_per_1000yen)
    total_scoles = 0
    result_type = ""
    rush_info = {}

    lot_mode = random.randint(1, 100)
    if lot_mode <= 50: # 50%で当たり
        total_scoles = 1800 - hit_inves
        result_type = "単発"
    else: # 50%でラッシュ分岐
        # ラッシュ突入
        rush_num, special_num, rush_raw_score = lot_special(99, 163)
        total_scoles = (rush_raw_score * 4)+1800 - hit_inves
        result_type = "ラッシュ"
        rush_info = {
            "rush_count": special_num,
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
            #data_to_insert["raw_rush_score"] = rush_info["raw_rush_score"]

        response = supabase.table("eva").insert(data_to_insert).execute()
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
        st.write(f"  - ラッシュ中獲得点数/玉数: {rush_info['raw_rush_score']}") 

    st.info("別のシミュレーションを実行するには、再度ボタンを押してください。")