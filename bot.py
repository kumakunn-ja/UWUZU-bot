import feedparser
import requests
import os
import json

# --- 設定エリア ---
# uwuzuのインスタンスURLとRSSフィードのURLを指定
UWUZU_INSTANCE = "https://uwuzu.ut-gov.f5.si/" # 自分の使っているサーバーURLに変更
 # 取得したいRSSフィードのURLに変更
 # 最後に投稿した記事を記録するファイル

RSS_URLS = [
    "https://www.gizmodo.jp/index.xml",
    "https://www.itmedia.co.jp/news/subindex/index.xml",
    "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "https://www.bbc.com/japanese/index.xml",
    "https://gori.me/feed"
]
# 各サイトの最後の投稿を記録するファイル（JSON形式に変更すると管理が楽です）
LAST_DATA_FILE = "last_links.json"

def post_to_uwuzu(text):
    token = os.environ.get("UWUZU_TOKEN")
    url = f"{UWUZU_INSTANCE}/api/ueuse/create"
    data = {"token": token, "text": text}
    try:
        response = requests.post(url, json=data)
        return response.status_code == 200
    except:
        return False

def main():
    # 前回の記録を読み込む（なければ空の辞書）
    last_data = {}
    if os.path.exists(LAST_DATA_FILE):
        with open(LAST_DATA_FILE, "r") as f:
            last_data = json.load(f)

    # リストにあるURLを一つずつチェック
    for rss_url in RSS_URLS:
        print(f"チェック中: {rss_url}")
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            continue

        latest_entry = feed.entries[0]
        title = latest_entry.title
        link = latest_entry.link

        # そのサイトの「前回のリンク」と比較
        if last_data.get(rss_url) != link:
            print(f"新着あり: {title}")
            content = f"【新着】{title}\n{link}"
            
            if post_to_uwuzu(content):
                # 記録を更新
                last_data[rss_url] = link
        else:
            print("新着なし")

    # 全サイトのチェックが終わったら、まとめて記録を保存
    with open(LAST_DATA_FILE, "w") as f:
        json.dump(last_data, f)

if __name__ == "__main__":
    main()
