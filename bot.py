import google.generativeai as genai
import requests
import time
import random
import os  # ファイルの存在確認用
import google.api_core.exceptions


# ==========================================
# 1. あなたの設定（ここを入力してください）
# ==========================================
API_KEYS = ["AIzaSyB6lTgjLo81QBatAHqD2WsMwCxcAnzie44","AIzaSyC5Yrq7CeDTDNMv_YO0z9Pvr7nE5FyJ3Iw","AIzaSyCPt6-Xdh3n5yI2PvUND1A-cAhTF5fkPHk", "AIzaSyAKioLzB4_NZBduHJ86KKTAUffxtUXarYg"]
UWUZU_TOKEN = "UUUTIbCOcasjSYCHttVu6EwUg0hyob8wy73q1Ig508Dpwkp1WfpXOG5Rnz2oQbq8"
DOMAIN = "uwuzu.ut-gov.f5.si"
BOT_ID = "kumakunnbot" # あなたのBotのID（@なし）





# 予備の返信リスト（レート制限中はこの中からランダム、または固定で返信）
BACKUP_REPLIES = [
    "（現在、レート制限を迎えましたAPIキーを変えるまで待っててください）",
    "（@kumakunn0411にお知らせください）",
    ]


# 最初に使うキーの番号
current_key_index = 0

def configure_genai():
    """現在のインデックスのキーでGeminiを設定する"""
    key = API_KEYS[current_key_index]
    genai.configure(api_key=key)
    print(f"--- APIキー設定完了 (Index: {current_key_index}) ---")
    return genai.GenerativeModel('gemini-1.5-flash')

# 初回設定
model = configure_genai()

# 既読IDを保存するファイル名
HISTORY_FILE = "replied_history.txt"

# 既読リストを読み込む
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        # ファイルから1行ずつ読み込んで集合(set)に変換
        replied_ids = set(f.read().splitlines())
    print(f"履歴ファイルを読み込みました。既読件数: {len(replied_ids)}件")
else:
    replied_ids = set()
    print("履歴ファイルが見つからないため、新規作成します。")

# ==========================================
# 2. 機能関数
# ==========================================

def save_id_to_file(uniqid):
    """返信済みのIDをファイルに追記する"""
    with open(HISTORY_FILE, "a") as f:
        f.write(uniqid + "\n")

def get_gemini_response(prompt):
    for i, key in enumerate(API_KEYS):
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text.strip(), False
        except google.api_core.exceptions.ResourceExhausted:
            print(f"⚠️ キー {i+1}番目 レート制限")
            continue
        except Exception as e:
            print(f"⚠️ キー {i+1}番目 エラー: {e}")
            continue
    return "（現在思考停止中…）", True

def get_mentions():
    url = f"https://{DOMAIN}/api/ueuse/mentions"
    payload = {"token": UWUZU_TOKEN, "limit": 5}
    try:
        res = requests.post(url, json=payload, timeout=10)
        data = res.json()
        mentions_list = []
        if isinstance(data, dict) and data.get('success'):
            for key, value in data.items():
                if key.isdigit():
                    mentions_list.append(value)
        return mentions_list
    except:
        return []

def bot_reply(text, target_uniqid):
    url = f"https://{DOMAIN}/api/ueuse/create"
    payload = {"token": str(UWUZU_TOKEN), "text": str(text), "replyid": str(target_uniqid)}
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res
    except:
        return None

# ==========================================
# 3. メインループ
# ==========================================
print(f"--- {BOT_ID} 稼働開始（履歴保存機能付き） ---")

while True:
    try:
        mentions = get_mentions()

        for m in mentions:
            current_uniqid = m.get('uniqid')
            sender_id = m.get('account', {}).get('username')

            # ファイルから読み込んだ既読リストに含まれていないかチェック
            if current_uniqid and current_uniqid not in replied_ids:
                if sender_id == BOT_ID:
                    replied_ids.add(current_uniqid)
                    save_id_to_file(current_uniqid) # 自分のも記録
                    continue

                content = m.get('text', '')
                print(f"【受信】 {sender_id}: {content}")

                prompt = f"あなたはuwuzuのBotです。@{sender_id} さんへ短く返信して。内容：{content}"
                ai_text, is_backup = get_gemini_response(prompt)

                final_text = f"@{sender_id} {ai_text.replace(f'@{BOT_ID}', '').strip()}"

                res = bot_reply(final_text, current_uniqid)

                if res and res.status_code == 200:
                    print(f"【完了】 {final_text}")
                    # メモリとファイルの両方に保存
                    replied_ids.add(current_uniqid)
                    save_id_to_file(current_uniqid)
                else:
                    print(f"【失敗】 送信エラー")

    except Exception as e:
        print(f"エラー: {e}")

    time.sleep(30)
