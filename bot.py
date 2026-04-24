import feedparser
import requests
import os

# --- 設定エリア ---
# uwuzuのインスタンスURLとRSSフィードのURLを指定
UWUZU_INSTANCE = "https://uwuzu.ut-gov.f5.si/" # 自分の使っているサーバーURLに変更
RSS_URL = "https://www.gizmodo.jp/index.xml"        # 取得したいRSSフィードのURLに変更
LAST_LINK_FILE = "last_link.txt"            # 最後に投稿した記事を記録するファイル

def post_to_uwuzu(text):
    """仕様に完全に合わせた投稿関数"""
    token = os.environ.get("UWUZU_TOKEN")
    
    # 仕様通りのエンドポイント
    url = f"{UWUZU_INSTANCE}/api/ueuse/create"
    
    # 必須パラメータをJSONで構成
    # 仕様書通りに token と text を入れる
    data = {
        "token": token,
        "text": text
    }
    
    try:
        # 認証ヘッダーを使わず、データの中にトークンを入れてPOSTする
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print("投稿成功！")
            return True
        else:
            print(f"投稿失敗。ステータスコード: {response.status_code}")
            print(f"エラー内容: {response.text}")
            return False
    except Exception as e:
        print(f"通信エラーが発生しました: {e}")
        return False

def main():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("記事が見つかりません。")
        return

    latest_entry = feed.entries[0]
    title = latest_entry.title
    link = latest_entry.link

    last_link = ""
    if os.path.exists(LAST_LINK_FILE):
        with open(LAST_LINK_FILE, "r") as f:
            last_link = f.read().strip()

    if link != last_link:
        # 投稿する文章を作る
        content = f"【新着】{title}\n{link}"
        
        if post_to_uwuzu(content):
            with open(LAST_LINK_FILE, "w") as f:
                f.write(link)
    else:
        print("新着記事はないよ。")

if __name__ == "__main__":
    main()
