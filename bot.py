import feedparser
import requests
import os
import json



# --- 設定項目（GitHub ActionsのSecretsから読み込む） ---
DOMAIN = "uwuzu.ut-gov.f5.si"
TOKEN = os.getenv("UWUZU_TOKEN")
INFO_API = f"https://{DOMAIN}/api/serverinfo-api"
CREATE_API = f"https://{DOMAIN}/api/ueuse/create"
STATE_FILE = "state.json"

def post_to_uwuzu(text):
    if not TOKEN: return
    payload = {"token": TOKEN, "text": text, "nsfw": False}
    requests.post(CREATE_API, data=json.dumps(payload), headers={'Content-Type': 'application/json'})

def monitor_server():
    # 前回の状態を読み込み
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
    else:
        state = {"last_notice_time": None, "last_user_count": None}

    try:
        response = requests.get(INFO_API)
        data = response.json()
        
        # 新規ユーザーチェック
        current_users = data['server_info']['usage']['users']
        if state["last_user_count"] and current_users > state["last_user_count"]:
            diff = current_users - state["last_user_count"]
            post_to_uwuzu(f"🔔 【新規参加】新たに {diff} 名の方が参加しました！現在のユーザー数は {current_users} 名です。")
        
        # お知らせチェック
        if data['server_notice']:
            latest = data['server_notice'][0]
            if state["last_notice_time"] and latest['datetime'] != state["last_notice_time"]:
                post_to_uwuzu(f"📢 【お知らせ】\n{latest['title']}\n\n{latest['note']}")
            state["last_notice_time"] = latest['datetime']

        state["last_user_count"] = current_users

        # 状態を保存
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_server()
