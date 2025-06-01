import random
import math

from supabase import create_client, Client
url: str = "https://pszefvosagdpzilocerq.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBzemVmdm9zYWdkcHppbG9jZXJxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4ODU1NTIsImV4cCI6MjA2MDQ2MTU1Mn0.nRw_Ev8VGVf_PvnQZ5Lk10JPYg3jaJwUWkGCmNO03fA"

supabase: Client = create_client(url, key)

def lot_norm(hatuatari):#通常時の抽選　引数：初当たり確率　戻り値：初当たりまでの回数
    attempts = 0 
    WINNING_NUMBER = 1
    while True:
        attempts += 1 
        drawn_number = random.randint(1, hatuatari) # 1から319までの整数をランダムに引く

        if drawn_number == WINNING_NUMBER:
           # print(f"{attempts}回目: 🎉 おめでとうございます！当たりです！ ")
            break 
    return attempts

def inves_money(hatuatari,kaitensu):#通常時の抽選にかかった金額を算出 引数:(確率,回転数)　戻値：初当たり回数と投資額
    hit_num = lot_norm(hatuatari) #回転数と初当たり回数から実際の金額を算出
    number = hit_num/kaitensu*1000
    divided_and_ceiled = math.ceil(number / 500)
    return hit_num,int(divided_and_ceiled * 500)#500円で切り上げて実際の貸代金額を算出

def lot_special(hatuatari,densapo):#ラッシュ時の抽選　引数：(確率,電サポ回数)　戻り値：出球
    attempts = 0 
    hit_attemps = 0
    special_attemps = 0
    scoles = 1500
    WINNING_NUMBER = 1
    while True:
        attempts += 1 
        drawn_number = random.randint(1, hatuatari) # 1からhatuatariまでの整数をランダムに引く
        if drawn_number == WINNING_NUMBER:
            drawn_number2 =random.randint(1,100)
            if drawn_number2 <4:
                scoles += 6000
                special_attemps +=1
                attempts - 0
            else:
                scoles += 3000
                hit_attemps +=1
                attempts = 0
        else:
            if attempts == densapo:
                break 
    return hit_attemps,special_attemps,scoles

###ゲームフロー
#1,初当たりまでの回数と総投資を決める。引数は初当たりと回転数
#2,50/100の抽選を行いチャージか初当たりを決める。(チャージ割合50%)
#3,当たりの場合、単発かラッシュか1/2でモードを決める。
#4,単発の場合、6000円をプラスして終わり
#5,ラッシュの場合、ラッシュのスペックで外れるまで続ける。引数は当選確率とラッシュ数
#　ラッシュ中は３%で6,000発の当たりを含める。
hit_num,hit_inves=inves_money(399,18)#初当たり回数と投資額を算出
lot_mode = random.randint(1,100)
if lot_mode <50:#49%で単発
    total_scoles =1200-hit_inves#1/2で出球300のチャージ当たりから投資額を引く
    supabase.table("ghole").insert({"hit_count":hit_num}).execute()
    print("😡チャージ 初当たり:"f"{hit_num}""　/結果:"f"{total_scoles}""円")
         
else:#51%でラッシュ
    lot_charge = random.randint(1,2)
    if lot_charge <2:#1/2で単発のモードをとる。
        total_scoles = 6000-hit_inves#1/2で出球1500発から投資額をひく
        supabase.table("ghole").insert({"hit_count":hit_num}).execute()
        print("☠️単発 初当たり:"f"{hit_num}""　/結果:"f"{total_scoles}""円") 

    else:
        rush_num,special_num,rush_resrt=lot_special(95,130)#ラッシュ回数と出球を算出
        total_scoles =4*rush_resrt-hit_inves#出球から投資額をひく
        supabase.table("ghole").insert({"hit_count":hit_num}).execute()
        print("🎉ラッシュ突入！🎉 初当たり:"f"{hit_num}""　/ラッシュ回数:"f"{rush_num}""　/6000ラッシュ回数:"f"{special_num}""　/結果"f"{total_scoles}""円")

        




