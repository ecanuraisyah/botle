import os
from aiogram import Bot, Dispatcher, types, executor
from dotenv import load_dotenv
import openai

# Load token dan API key
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Init bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
openai.api_key = OPENAI_API_KEY

# Fitur 1: Jawab soal matematika
@dp.message_handler(commands=['math'])
async def handle_math(message: types.Message):
    question = message.get_args()
    if not question:
        await message.reply("Kirim soalnya seperti ini:\n`/math hitung integral x^2 dx`", parse_mode="Markdown")
        return

    prompt = f"Jelaskan langkah demi langkah untuk soal matematika ini:\n{question}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    answer = response['choices'][0]['message']['content']
    await message.reply(answer)

# Fitur 2: Terjemahkan
@dp.message_handler(commands=['translate'])
async def handle_translate(message: types.Message):
    args = message.get_args().split()
    if len(args) < 3:
        await message.reply("Format:\n`/translate <from> <to> <text>`\nContoh: `/translate id en aku lapar`", parse_mode="Markdown")
        return
    source, target, *text = args
    content = " ".join(text)
    prompt = f"Terjemahkan dari {source} ke {target}:\n{content}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    translated = response['choices'][0]['message']['content']
    await message.reply(translated)

# Fitur 3: Chatbot
@dp.message_handler(commands=['chat'])
async def handle_chat(message: types.Message):
    user_input = message.get_args()
    if not user_input:
        await message.reply("Gunakan seperti ini:\n`/chat jelaskan teori relativitas`", parse_mode="Markdown")
        return

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}],
        temperature=0.7,
    )
    answer = response['choices'][0]['message']['content']
    await message.reply(answer)

# Start polling
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
