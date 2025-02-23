# 📢 YouTube Video Notifier Bot

This project is an **asynchronous Python bot** that monitors YouTube channels and sends updates to a **Telegram chat**. It is built using **aiohttp**, **asyncio**, and **Telegram Bot API**.

## 🚀 Features
- ✅ Fetch latest videos from multiple YouTube channels
- ✅ Convert timestamps to human-readable format (e.g., "2 days ago")
- ✅ Send formatted messages to a Telegram chat
- ✅ Uses **aiohttp** for non-blocking network requests
- ✅ Supports environment variables for API keys and credentials

## 📌 Technologies Used
- **Python 3.9+**
- **aiohttp** - For asynchronous HTTP requests
- **asyncio** - To handle concurrency efficiently
- **YouTube Data API v3** - To fetch video updates
- **Telegram Bot API** - To send notifications
- **Logging** - For debugging and error tracking

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/youtube-telegram-bot.git
cd youtube-telegram-bot
```

### 2️⃣ Create a Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3️⃣ Set Up Environment Variables
Create a `.env` file and add:
```ini
YOUTUBE_API_KEY=your_youtube_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 4️⃣ Run the Bot
```bash
python bot.py
```

## 📦 Docker Setup
You can also run this bot inside a **Docker container**.
```bash
# Build the Docker image
docker build -t youtube-telegram-bot .

# Run the container
docker run -d --env-file .env youtube-telegram-bot
```

## 📌 How It Works
1. The bot fetches YouTube channel IDs using **channel usernames**.
2. It retrieves the **latest videos** from each channel.
3. It formats the results and sends a message to a **Telegram group/chat**.
4. The bot runs asynchronously, ensuring **efficient API calls**.

## 🔧 TODOs & Improvements
- ✅ Improve error handling for API failures
- ✅ Implement scheduled checks using `asyncio`
- 🚀 Add database support to track previously sent videos
- 📌 Allow users to dynamically add/remove channels

## 🤝 Contributions
Feel free to **fork** this repo, **open issues**, or submit **pull requests** to improve this project.

---

📌 **Note:** This project is for **educational purposes** and should comply with YouTube & Telegram API policies.

🚀 *Happy Coding!* 🎥🤖

