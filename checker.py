import requests
import os
from bs4 import BeautifulSoup

MANGA_URL = "https://manhwaclan.com/manga/the-beginning-after-the-end/"
LAST_CHAPTER_FILE = "last_chapter.txt"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def get_latest_chapter():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(MANGA_URL, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    chapters = soup.select("li.wp-manga-chapter a")
    if not chapters:
        return None, None

    latest = chapters[0]
    chapter_title = latest.text.strip()
    chapter_url = latest["href"]
    return chapter_title, chapter_url

def read_last_chapter():
    try:
        with open(LAST_CHAPTER_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def save_last_chapter(chapter_title):
    with open(LAST_CHAPTER_FILE, "w") as f:
        f.write(chapter_title)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def main():
    chapter_title, chapter_url = get_latest_chapter()
    if not chapter_title:
        print("No chapters found.")
        return

    last = read_last_chapter()
    print(f"Latest: {chapter_title} | Last seen: {last}")

    if chapter_title != last:
        msg = (
            f"📖 <b>New Chapter Alert!</b>\n\n"
            f"<b>The Beginning After the End</b>\n"
            f"{chapter_title} is out!\n\n"
            f"🔗 <a href='{chapter_url}'>Read it on ManhwaClan</a>"
        )
        send_telegram(msg)
        save_last_chapter(chapter_title)
        print(f"Notified for {chapter_title}!")
    else:
        print("No new chapter.")

if __name__ == "__main__":
    main()
