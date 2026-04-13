import requests
import os

MANGA_ID = "4ada20eb-085a-491a-8c49-477ab42014d7"
LAST_CHAPTER_FILE = "last_chapter.txt"
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def get_latest_chapter():
    url = "https://api.mangadex.org/chapter"
    params = {
        "manga": MANGA_ID,
        "translatedLanguage[]": "en",
        "order[chapter]": "desc",
        "limit": 1,
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    if not data["data"]:
        return None, None
    chapter = data["data"][0]
    chapter_num = chapter["attributes"]["chapter"]
    chapter_id = chapter["id"]
    return chapter_num, chapter_id

def read_last_chapter():
    try:
        with open(LAST_CHAPTER_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def save_last_chapter(chapter_num):
    with open(LAST_CHAPTER_FILE, "w") as f:
        f.write(chapter_num)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def main():
    chapter_num, chapter_id = get_latest_chapter()
    if not chapter_num:
        print("No chapters found.")
        return

    last = read_last_chapter()
    print(f"Latest: {chapter_num} | Last seen: {last}")

    if chapter_num != last:
        link = f"https://mangadex.org/chapter/{chapter_id}"
        msg = (
            f"📖 <b>New Chapter Alert!</b>\n\n"
            f"<b>The Beginning After the End</b>\n"
            f"Chapter <b>{chapter_num}</b> is out!\n\n"
            f"🔗 <a href='{link}'>Read it on MangaDex</a>"
        )
        send_telegram(msg)
        save_last_chapter(chapter_num)
        print(f"Notified for chapter {chapter_num}!")
    else:
        print("No new chapter.")

if __name__ == "__main__":
    main()
