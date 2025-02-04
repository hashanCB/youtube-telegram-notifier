import os
import aiohttp
import asyncio
from datetime import datetime, timezone
from telegram import Bot
from typing import List, Tuple, Optional
from aiohttp import ClientSession
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
API_KEY = os.getenv("YOUTUBE_API_KEY")  # Updated to match workflow env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# YouTube channels to monitor
CHANNEL_USERNAMES = [
    "Raamuwa",
    "XraidPodcast",
    "TechTrackShow",
    "RandikaWijesinghe",
    "johnnyharris",
    "TheDiaryOfACEO",
    "SanjayaElvitigala"
]

class YouTubeError(Exception):
    """Custom exception for YouTube API related errors"""
    pass

def time_ago(published_at: str) -> str:
    """
    Convert published date to relative time (e.g., '2 days ago').
    
    Args:
        published_at (str): ISO format datetime string
        
    Returns:
        str: Human readable time difference
    """
    try:
        published_time = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        published_time = published_time.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - published_time
        seconds = diff.total_seconds()

        intervals = [
            (604800, "weeks"),
            (86400, "days"),
            (3600, "hours"),
            (60, "minutes")
        ]

        for seconds_in_unit, unit in intervals:
            if seconds >= seconds_in_unit:
                value = int(seconds // seconds_in_unit)
                return f"{value} {unit} ago"
                
        return "just now"
    except ValueError as e:
        logger.error(f"Error parsing date {published_at}: {e}")
        return "unknown time ago"

async def get_channel_id(username: str, session: ClientSession) -> Optional[str]:
    """
    Fetch channel ID from username.
    
    Args:
        username (str): YouTube channel username
        session (ClientSession): Aiohttp session
        
    Returns:
        Optional[str]: Channel ID if found, None otherwise
    """
    if not API_KEY:
        raise YouTubeError("YouTube API key not found in environment variables")
        
    url = f"https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "id",
        "forUsername": username,
        "key": API_KEY
    }
    
    try:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                logger.error(f"YouTube API error for {username}: {await response.text()}")
                return None
                
            data = await response.json()
            if "items" in data and data["items"]:
                return data["items"][0]["id"]
            logger.warning(f"No channel found for username: {username}")
            return None
    except aiohttp.ClientError as e:
        logger.error(f"Network error while fetching channel ID for {username}: {e}")
        return None

async def get_latest_videos(channel_id: str, session: ClientSession) -> List[Tuple[str, str]]:
    """
    Fetch latest video titles and publish dates.
    
    Args:
        channel_id (str): YouTube channel ID
        session (ClientSession): Aiohttp session
        
    Returns:
        List[Tuple[str, str]]: List of (title, relative_time) tuples
    """
    url = f"https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": 8,
        "type": "video"  # Only fetch videos, not playlists or channels
    }
    
    try:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                logger.error(f"YouTube API error for channel {channel_id}: {await response.text()}")
                return []
                
            data = await response.json()
            videos = []
            
            if "items" in data:
                for item in data["items"]:
                    snippet = item["snippet"]
                    title = snippet["title"]
                    published_at = snippet["publishedAt"]
                    videos.append((title, time_ago(published_at)))
            return videos
    except aiohttp.ClientError as e:
        logger.error(f"Network error while fetching videos for channel {channel_id}: {e}")
        return []

async def send_to_telegram(message: str) -> None:
    """
    Send message to Telegram in chunks if it's too long.
    
    Args:
        message (str): Message to send
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError("Telegram credentials not found in environment variables")
        
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        max_length = 4096  # Telegram's message length limit
        
        for i in range(0, len(message), max_length):
            chunk = message[i:i + max_length]
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=chunk,
                parse_mode='HTML'  # Enable HTML formatting
            )
    except Exception as e:
        logger.error(f"Error sending message to Telegram: {e}")
        raise

async def fetch_and_send_videos() -> None:
    """Fetch videos and send to Telegram."""
    message = "<b>🎥 Latest YouTube Videos Update</b>\n\n"
    
    async with aiohttp.ClientSession() as session:
        for username in CHANNEL_USERNAMES:
            try:
                channel_id = await get_channel_id(username, session)
                if channel_id:
                    message += f"📺 <b>Channel: {username}</b>\n"
                    videos = await get_latest_videos(channel_id, session)
                    
                    if videos:
                        for i, (title, published_time) in enumerate(videos, 1):
                            message += f"{i}. {title} ({published_time})\n"
                    else:
                        message += "No recent videos found\n"
                else:
                    message += f"⚠️ Could not find channel ID for: {username}\n"
            except Exception as e:
                logger.error(f"Error processing channel {username}: {e}")
                message += f"⚠️ Error processing channel {username}\n"
            
            message += "\n"  # Add spacing between channels
            
        try:
            await send_to_telegram(message)
            logger.info("Successfully sent update to Telegram")
        except Exception as e:
            logger.error(f"Failed to send update to Telegram: {e}")

def main():
    """Main entry point with error handling."""
    try:
        asyncio.run(fetch_and_send_videos())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Script failed with error: {e}")
        raise

if __name__ == "__main__":
    main()