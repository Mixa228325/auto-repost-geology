
import os
import time
from bs4 import BeautifulSoup
import requests
from googletrans import Translator
from telegram import Bot

TOKEN = os.getenv('TOKEN')
CHANNEL = os.getenv('CHANNEL')
URL = os.getenv('URL', 'https://www.geologyin.com')
INTERVAL = int(os.getenv('INTERVAL', 900))  # default 900 секунд = 15 минут

bot = Bot(token=TOKEN)
translator = Translator()
last_title = None

def get_latest_article():
    resp = requests.get(URL, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    item = soup.select_one('.item-list .items-row h2 a')
    if not item:
        return None
    title = item.get_text(strip=True)
    href = item['href']
    link = href if href.startswith('http') else (URL.rstrip('/') + '/' + href.lstrip('/'))
    return title, link

def get_description(link):
    resp = requests.get(link, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    p = soup.select_one('.item-page p')
    return p.get_text(strip=True) if p else ''

def translate(text, code):
    try:
        return translator.translate(text, dest=code).text
    except:
        return text

def main():
    global last_title
    while True:
        try:
            article = get_latest_article()
            if article:
                title, link = article
                if title != last_title:
                    desc = get_description(link)
                    title_ru = translate(title, 'ru')
                    title_uz = translate(title, 'uz')
                    desc_ru = translate(desc, 'ru')
                    desc_uz = translate(desc, 'uz')
                    message = (
                        f"🌋 {title_ru}\n"
                        f"🇺🇿 {title_uz}\n\n"
                        f"📄 {desc_ru}\n"
                        f"{desc_uz}\n\n"
                        f"🔗 {link}\n"
                        "#геология #новости"
                    )
                    bot.send_message(chat_id=CHANNEL, text=message)
                    last_title = title
        except Exception as e:
            print("Ошибка:", e)
        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
