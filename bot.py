import feedparser
import requests
import os

# --- 設定エリア ---
# uwuzuのインスタンスURLとRSSフィードのURLを指定
UWUZU_INSTANCE = "https://uwuzu.ut-gov.f5.si/" # 自分の使っているサーバーURLに変更
RSS_URL = "https://www.gizmodo.jp/index.xml"        # 取得したいRSSフィードのURLに変更
LAST_LINK_FILE = "last_link.txt"            # 最後に投稿した記事を記録するファイル

def main():
    # RSSフィードを解析
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("記事が見つかりませんでした。")
        return

    # 最新の記事を取得
    latest_entry = feed.entries[0]
    title = latest_entry.title
    link = latest_entry.link

    # 前回の投稿内容を確認
    last_link = ""
    if os.path.exists(LAST_LINK_FILE):
        with open(LAST_LINK_FILE, "r") as f:
            last_link = f.read().strip()

    # 新着チェック
    if link != last_link:
        print(f"新着記事を発見: {title}")
        content = f"【新着記事】\n{title}\n{link}"
        
        if post_to_uwuzu(content):
            print("uwuzuへの投稿に成功しました。")
            # 最後に投稿したリンクを保存
            with open(LAST_LINK_FILE, "w") as f:
                f.write(link)
        else:
            print("投稿に失敗しました。")
    else:
        print("新着記事はありません。")

if __name__ == "__main__":
    main()



def post_to_uwuzu(text):
    """uwuzu専用APIを使って投稿する"""
    token = os.environ.get("UWUZU_TOKEN")
    if not token:
        print("Error: UWUZU_TOKEN が設定されていません。")
        return False
    
    # 仕様に基づいたURL
    url = f"{UWUZU_INSTANCE}/api/ueuse/create"
    
    # 必須パラメータをJSONで送信
    data = {
        "token": token,
        "text": text
    }
    
    try:
        # POSTリクエストを送信
        response = requests.post(url, json=data)
        
        # 成功したかどうかの確認
        if response.status_code == 200:
            return True
        else:
            print(f"投稿失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False
