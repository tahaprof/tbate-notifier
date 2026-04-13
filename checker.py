import requests
import os
from bs4 import BeautifulSoup

SITE_URL = "https://w17.thebeginningaftertheendmanga.com/"
LAST_CHAPTER_FILE = "last_chapter.txt"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
DISCORD_CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]

def get_latest_chapter():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    resp = requests.get(SITE_URL, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    links = soup.select("ul li a[href*='chapter']")
    if not links:
        return None, None

    latest = links[0]
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

def send_discord(message):
    url = f"https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"content": message}
    response = requests.post(url, headers=headers, json=payload)
    print(f"Discord response: {response.status_code} - {response.text}")

def main():
    chapter_title, chapter_url = get_latest_chapter()
    if not chapter_title:
        print("No chapters found.")
        return

    last = read_last_chapter()
    print(f"Latest: {chapter_title} | Last seen: {last}")

    if chapter_title != last:
        telegram_msg = (
            f"📖 <b>New Chapter Alert!</b>\n\n"
            f"<b>The Beginning After the End</b>\n"
            f"{chapter_title} is out!\n\n"
            f"🔗 <a href='{chapter_url}'>Read it here</a>"
        )
        discord_msg = (
            f"📖 **New Chapter Alert!**\n\n"
            f"**The Beginning After the End**\n"
            f"{chapter_title} is out!\n\n"
            f"🔗 Read it here: {chapter_url}"
        )
        send_telegram(telegram_msg)
        send_discord(discord_msg)
        save_last_chapter(chapter_title)
        print(f"Notified for {chapter_title}!")
    else:
        print("No new chapter.")

if __name__ == "__main__":
    main()
