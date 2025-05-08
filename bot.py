import os
from aiogram import Bot, Dispatcher, types, executor
import openai
from collections import defaultdict

# Ambil token dari environment (Railway)
BOT_TOKEN = os.environ["BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Setup bot dan OpenAI
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
openai.api_key = OPENAI_API_KEY

# Memori chat per user
chat_history = defaultdict(list)
active_chat_users = set()

# ======== FITUR MATEMATIKA ==========
@dp.message_handler(commands=['math'])
async def handle_math(message: types.Message):
    question = message.get_args()
    if not question:
        await message.reply("Kirim soalnya seperti ini:\n`/math hitung integral x^2 dx`", parse_mode="Markdown")
        return

    prompt = f"Jelaskan langkah demi langkah untuk soal matematika berikut:\n{question}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    answer = response['choices'][0]['message']['content']
    await message.reply(answer)

# ======== FITUR TRANSLASI ==========
@dp.message_handler(commands=['translate'])
async def handle_translate(message: types.Message):
    args = message.get_args().split()
    if len(args) < 3:
        await message.reply("Format:\n`/translate <dari> <ke> <teks>`\nContoh: `/translate id en aku lapar`", parse_mode="Markdown")
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

# ======== MODE CHAT INTERAKTIF ==========
@dp.message_handler(commands=["chat_on"])
async def enable_chat_mode(message: types.Message):
    user_id = message.from_user.id
    active_chat_users.add(user_id)
    await message.reply("✅ Mode chat aktif! Kirim pesan apa saja dan aku akan membalas.")

@dp.message_handler(commands=["chat_off"])
async def disable_chat_mode(message: types.Message):
    user_id = message.from_user.id
    active_chat_users.discard(user_id)
    chat_history[user_id].clear()
    await message.reply("❌ Mode chat dinonaktifkan. Chat AI dihentikan.")

# ======== PESAN UMUM (CHAT AI) ==========
@dp.message_handler()
async def handle_general_message(message: types.Message):
    user_id = message.from_user.id
    if user_id not in active_chat_users:
        return  # Abaikan jika mode chat tidak aktif

    user_message = message.text
    history = chat_history[user_id]

    # Tambahkan pesan user ke histori
    history.append({"role": "user", "content": user_message})

    # Ambil 10 percakapan terakhir
    context = history[-10:]

    # Balas dari OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=context,
        temperature=0.7
    )
    reply = response['choices'][0]['message']['content']
    history.append({"role": "assistant", "content": reply})
    await message.reply(reply)

# ======== START BOT ==========
if __name__ == "__main__":
    print("Bot berjalan...")
    executor.start_polling(dp, skip_updates=True)
