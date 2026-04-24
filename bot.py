import feedparser
import requests
import os

# --- 設定エリア ---
# uwuzuのインスタンスURLとRSSフィードのURLを指定
UWUZU_INSTANCE = "https://uwuzu.example.com" # 自分の使っているサーバーURLに変更
RSS_URL = "https://example.com/feed"        # 取得したいRSSフィードのURLに変更
LAST_LINK_FILE = "last_link.txt"            # 最後に投稿した記事を記録するファイル

def post_to_uwuzu(text):
    """uwuzuのAPIを使って投稿する"""
    token = os.environ.get("UWUZU_TOKEN")
    if not token:
        print("Error: UWUZU_TOKEN が設定されていません。")
        return False
    
    url = f"{UWUZU_INSTANCE}/api/v1/statuses"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"status": text}
    
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

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
