"""
技術に関する最新のニュース記事を取得し、
フォーマットしてLINEメッセージとして送信する。

処理フローは以下になる。
1. RSS / Atomフィードからの技術記事の取得
2. News APIを利用した技術記事の取得
3. 取得した記事をフォーマットしてLINEメッセージとして送信
4. AWS Lambdaでの実行
"""

import json
import requests
import feedparser
import os
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# 環境変数を取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = os.getenv('LINE_USER_ID')
NEWSAPI_KEY  = os.getenv('NEWSAPI_KEY')
NEWSAPI_URL  = os.getenv('NEWSAPI_URL')
LINE_BOT_PUSH_URL = os.getenv('LINE_BOT_PUSH_URL')
PUBLICKEY_URL = os.getenv('PUBLICKEY_URL')
ZENN_URL      = os.getenv('ZENN_URL')
QIITA_URL     = os.getenv('QIITA_URL')

# ---------------------------------------------------------------------------------
# 内部関数
# ---------------------------------------------------------------------------------

def get_rss_feed(url):
    """
    RSS / Atomフィードを解析(パース)してサイトの新着記事などの情報を抽出

    Args:
        url (string)
    
    Returns:
        記事配列
    """

    feed = feedparser.parse(url)
    articles = []
    
    for entry in feed.entries[:5]:
        articles.append({
            'title': entry.title, 
            'link': entry.link
        })

    return articles

def get_news_from_api(article_count=5):
    """
    News APIから技術に関する記事を取得する

    Args:
        article_count (int): 取得するニュース記事の数
    
    Returns:
        ニュース記事配列
    """
    
    news_api_key  = NEWSAPI_KEY
    news_url      = NEWSAPI_URL
    url = f'{news_url}?category=technology&apiKey={news_api_key}&language=en'
    
    response  = requests.get(url)
    news_data = response.json()
    articles  = news_data['articles']
    news_list = [{
        'title': article['title'], 
        'link': article['url']
    } for article in articles[:article_count]]

    return news_list

def format_message(articles):
    """
    Messageを加工する

    Args:
        articles (list): ニュース記事のリスト。各記事は辞書形式で 'title' と 'link' を含む。
    
    Returns:
         str: フォーマットされたメッセージ
    """
    message = "今日のITニュース\n\n"
    
    for i, article in enumerate(articles, 1):
        message += f"{i}. {article['title']}\n{article['link']}\n\n"
    
    return message

def send_line_message(message):
    """
    LINE Messageを送信する

    Args:
        message (str): 送信したいメッセージ
    
    Returns:
        None
    """
    line_api_url = LINE_BOT_PUSH_URL
    line_user_id = LINE_USER_ID
    line_channel_access_token = LINE_CHANNEL_ACCESS_TOKEN
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {line_channel_access_token}'
    }
    payload = {
        'to': line_user_id,
        'messages': [{
            'type': 'text',
            'text': message
        }]
    }
    
    response = requests.post(line_api_url, headers=headers, json=payload)
    print(response.status_code, response.text)

# ---------------------------------------------------------------------------------

def main():
    """
    ニュースを取得し、フォーマットしてLINEに送信する
    """
    publickey_url = PUBLICKEY_URL
    zenn_url      = ZENN_URL
    qiita_url     = QIITA_URL
    
    publickey_articles = get_rss_feed(publickey_url)
    zenn_articles      = get_rss_feed(zenn_url)
    qiita_articles     = get_rss_feed(qiita_url)
    overseas_news      = get_news_from_api()
    
    all_articles = publickey_articles + zenn_articles + qiita_articles + overseas_news
    
    message = format_message(all_articles)
    send_line_message(message)

def lambda_handler(event, context):
    """
    AWS Lambdaのエントリポイント

    Args:
        event (dict): Lambda 関数に渡されるイベントデータ
        context (object): ランタイム情報を提供するコンテキストオブジェクト
    
    Returns:
        dict: ステータスコードとメッセージを含むレスポンス
    """
    
    main()
    return {
        'statusCode': 200,
        'body': json.dumps('News sent successfully!')
    }

if __name__ == "__main__":
    main()