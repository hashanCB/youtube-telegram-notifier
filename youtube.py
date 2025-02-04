import os
import aiohttp
import asyncio
from datetime import datetime, timezone
from telegram import Bot

# Replace with your YouTube Data API key and Telegram bot token
API_KEY = os.getenv("API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# List of YouTube channel usernames
CHANNEL_USERNAMES = [
    "Raamuwa",
    "XraidPodcast",
    "TechTrackShow",
    "RandikaWijesinghe",
    "johnnyharris",
    "TheDiaryOfACEO",
    "SanjayaElvitigala"
]

def time_ago(published_at):
    """Convert published date to relative time (e.g., '2 days ago')."""
    published_time = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
    published_time = published_time.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = now - published_time

    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    elif seconds < 604800:
        return f"{int(seconds // 86400)} days ago"
    else:
        return f"{int(seconds // 604800)} weeks ago"

async def get_channel_id(username, session):
    """Fetch channel ID from username."""
    url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forUsername={username}&key={API_KEY}"
    async with session.get(url) as response:
        data = await response.json()
        if "items" in data:
            return data["items"][0]["id"]
    return None

async def get_latest_videos(channel_id, session):
    """Fetch latest 3 video titles and publish dates."""
    url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={channel_id}&part=snippet&order=date&maxResults=8"
    async with session.get(url) as response:
        data = await response.json()

    videos = []
    if "items" in data:
        for item in data["items"]:
            title = item["snippet"]["title"]
            published_at = item["snippet"]["publishedAt"]
            videos.append((title, time_ago(published_at)))
    return videos

async def send_to_telegram(message):
    """Send message to Telegram in chunks if it's too long."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    max_length = 4096  # Telegram's message length limit
    for i in range(0, len(message), max_length):
        chunk = message[i:i + max_length]
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=chunk)

async def fetch_and_send_videos():
    """Fetch videos and send to Telegram."""
    message = ""
    async with aiohttp.ClientSession() as session:
        for username in CHANNEL_USERNAMES:
            channel_id = await get_channel_id(username, session)
            if channel_id:
                message += f"\n📺 Channel: {username}\n"
                videos = await get_latest_videos(channel_id, session)
                for i, (title, published_time) in enumerate(videos, 1):
                    message += f"{i}. {title} ({published_time})\n"
            else:
                message += f"\n⚠️ Could not find channel ID for: {username}\n"

    await send_to_telegram(message)

if __name__ == "__main__":
    asyncio.run(fetch_and_send_videos())
