import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from bs4 import BeautifulSoup
import requests
import sqlite3
from config import token

bot = Bot(token=token)
dp = Dispatcher()

conn = sqlite3.connect('news.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, news TEXT UNIQUE)''')
conn.commit()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Используй команду /news чтобы получить новости на сегодня")

@dp.message(Command('news'))
async def get_news(message: types.Message):
    response = requests.get("https://24.kg/")
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = soup.find_all("div", class_="one")
    news_list = []

    for news in news_items:
        news_text = news.get_text(strip=True)
        cursor.execute("SELECT id FROM news WHERE news = ?", (news_text,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO news (news) VALUES (?)", (news_text,))
            conn.commit()
            news_list.append(news_text)

    await message.answer("\n\n".join(news_list) if news_list else "Новых новостей не найдено")

@dp.message()
async def echo(message: types.Message):
    await message.answer("Пиши /news чтобы узнать новости")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
