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




def main():
    last_data = load_last_data()
    all_new_content = ""  # 全体の投稿内容を貯める変数

    for rss_url in RSS_URLS:
        feed = feedparser.parse(rss_url)
        if not feed.entries:
            continue

        site_title = feed.feed.title  # サイト名（GizmodoやNHKニュースなど）を取得
        site_posts = []

        # 各サイトの最新3件をチェック（まとめすぎると長くなるので3件くらいがおすすめ）
        for entry in feed.entries[:3]:
            raw_link = entry.link.split('?')[0]
            link = raw_link.replace("http://", "https://")
            
            if last_data.get(rss_url) != link:
                title = entry.title
                safe_link = link.replace("_", "\\_")
                site_posts.append(f"・{title}\n  {safe_link}")
                
                # そのサイトの最新記事として記憶
                if entry == feed.entries[0]:
                    last_data[rss_url] = link

        # このサイトに新着があれば、見出し付きで追加
        if site_posts:
            all_new_content += f"【{site_title}】\n" + "\n".join(site_posts) + "\n\n"

    # 全サイト分をまとめて1回だけ投稿
    if all_new_content:
        # 先頭にタイトルをつける
        final_message = "📢 新着ニュースまとめ\n\n" + all_new_content.strip()
        
        if post_to_uwuzu(final_message):
            save_last_data(last_data)
            print("サイトごとにまとめて投稿しました！")
