import feedparser
import requests
import os
import json

# --- 設定エリア ---
UWUZU_INSTANCE = "https://uwuzu.ut-gov.f5.si/"
RSS_URLS = [
    "https://rss.app/feeds/N4ZlfFqIWQVAMvsa.xml",
    "https://www.itmedia.co.jp/news/subindex/index.xml",
    "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "https://www.bbc.com/japanese/index.xml",
    "https://gori.me/feed"
]
LAST_DATA_FILE = "last_links.json"

def load_last_data():
    """既読URLのリストを読み込む"""
    if os.path.exists(LAST_DATA_FILE):
        try:
            with open(LAST_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_last_data(data):
    """既読URLのリストを保存（最新の50件程度に絞る）"""
    with open(LAST_DATA_FILE, "w", encoding="utf-8") as f:
        # 無限に肥大化しないよう、最新50件のみ保持
        json.dump(data[-50:], f, ensure_ascii=False, indent=4)

def post_to_uwuzu(message):
    api_key = os.getenv("UWUZU_TOKEN")
    if not api_key:
        print("Error: UWUZU_TOKEN が設定されていません。")
        return False

    url = f"{UWUZU_INSTANCE.rstrip('/')}/api/ueuse/create"
    payload = {
        "token": api_key,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"エラー発生: {e}")
        return False

def main():
    # last_data を既読URLの「リスト」として扱う
    posted_links = load_last_data()
    new_posted_links = []
    all_new_content = ""

    for rss_url in RSS_URLS:
        try:
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                continue

            site_title = feed.feed.title if hasattr(feed.feed, 'title') else "不明なサイト"
            site_posts = []

            # 直近3件をチェック
            for entry in feed.entries[:8]:
                raw_link = entry.link.split('?')[0]
                link = raw_link.replace("http://", "https://")
                
                # リストの中にリンクが存在するかチェック
                if link not in posted_links:
                    title = entry.title
                    safe_link = link.replace("_", "\\_")
                    site_posts.append(f"・{title}\n  {safe_link}")
                    
                    # 今回投稿するリストに追加（既読にする）
                    new_posted_links.append(link)

            if site_posts:
                all_new_content += f"【{site_title}】\n" + "\n".join(site_posts) + "\n\n"
        except Exception as e:
            print(f"RSS取得エラー ({rss_url}): {e}")

    if all_new_content:
        final_message = "📢 新着ニュースまとめ\n\n" + all_new_content.strip()
        
        if post_to_uwuzu(final_message):
            # 既存の既読リストに、今回新しく投稿した分を合流させて保存
            save_last_data(posted_links + new_posted_links)
            print("新着記事を投稿しました！")
    else:
        print("新しい記事はありませんでした。")

if __name__ == "__main__":
    main()
