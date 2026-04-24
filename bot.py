import feedparser
import requests
import os
import json

# --- 設定エリア ---
UWUZU_INSTANCE = "https://uwuzu.ut-gov.f5.si/"
RSS_URLS = [
    "https://www.gizmodo.jp/index.xml",
    "https://www.itmedia.co.jp/news/subindex/index.xml",
    "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "https://www.bbc.com/japanese/index.xml",
    "https://gori.me/feed"
]
LAST_DATA_FILE = "last_links.json"

def load_last_data():
    """前回の投稿データを読み込む"""
    if os.path.exists(LAST_DATA_FILE):
        try:
            with open(LAST_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_last_data(data):
    """今回の投稿データを保存する"""
    with open(LAST_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def post_to_uwuzu(message):
    """uwuzuに投稿する"""
    # GitHub ActionsのSecretsに設定したAPIキーを取得
    api_key = os.getenv("UWUZU_INSTANCE")
    if not api_key:
        print("Error: UWUZU_API_KEY が設定されていません。")
        return False

    url = f"{UWUZU_INSTANCE.rstrip('/')}/api/v1/posts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"text": message}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            return True
        else:
            print(f"投稿失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"エラー発生: {e}")
        return False

def main():
    last_data = load_last_data()
    all_new_content = ""

    for rss_url in RSS_URLS:
        try:
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                continue

            # サイト名を取得
            site_title = feed.feed.title if hasattr(feed.feed, 'title') else "不明なサイト"
            site_posts = []

            # 各サイトの最新3件をチェック
            for entry in feed.entries[:3]:
                raw_link = entry.link.split('?')[0]
                link = raw_link.replace("http://", "https://")
                
                # 未読チェック
                if last_data.get(rss_url) != link:
                    title = entry.title
                    # Markdown対策
                    safe_link = link.replace("_", "\\_")
                    site_posts.append(f"・{title}\n  {safe_link}")
                    
                    # そのサイトの最新記事を記憶（1番上の記事のみ）
                    if entry == feed.entries[0]:
                        last_data[rss_url] = link

            # 新着があれば追加
            if site_posts:
                all_new_content += f"【{site_title}】\n" + "\n".join(site_posts) + "\n\n"
        except Exception as e:
            print(f"RSS取得エラー ({rss_url}): {e}")

    # まとめて1回だけ投稿
    if all_new_content:
        final_message = "📢 新着ニュースまとめ\n\n" + all_new_content.strip()
        
        # 文字数制限（念のため）を考慮して500文字程度でカットするか、そのまま送る
        if post_to_uwuzu(final_message):
            save_last_data(last_data)
            print("まとめて投稿しました！")
    else:
        print("新しい記事はありませんでした。")

if __name__ == "__main__":
    main()
