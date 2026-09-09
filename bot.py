import os
import random
import json
import datetime
from zoneinfo import ZoneInfo
from threading import Thread
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

CARDS = [
    "🎁 SURPRISE!\n+$3 к дневному заработку!",
    "💰 JACKPOT!\n×2 дневной заработок!\nБыло $7 → сегодня $14!",
    "😎 БЕЗ ИЗМЕНЕНИЙ\nОбычный день. Всё по плану.\n+$0",
    "🌴 EASY DAY!\nОдно из пяти заданий можно пропустить сегодня.",
    "❤️ ПАПИН ПОДАРОК!\n−$2 с папиного дневного счёта → дочке +$2!"
]

PLAY_DAYS = [0, 2, 4]   # понедельник=0, среда=2, пятница=4
REST_DAY = 6            # воскресенье=6

# Часовой пояс Нячанга (Вьетнам). Игра идёт по времени дочери.
NHATRANG = ZoneInfo("Asia/Ho_Chi_Minh")

PLAYED_FILE = "played.json"


def today_nhatrang():
    """Текущая дата по времени Нячанга."""
    return datetime.datetime.now(NHATRANG).date()


def weekday_nhatrang():
    """День недели по времени Нячанга (понедельник=0 ... воскресенье=6)."""
    return today_nhatrang().weekday()


def load_played():
    try:
        with open(PLAYED_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_played(data):
    with open(PLAYED_FILE, "w") as f:
        json.dump(data, f)


def already_played_today(chat_id):
    data = load_played()
    today = today_nhatrang().isoformat()
    return data.get(str(chat_id)) == today


def mark_played_today(chat_id):
    data = load_played()
    data[str(chat_id)] = today_nhatrang().isoformat()
    save_played(data)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Привет!\n\n"
        "Викторина выходит по понедельникам, средам и пятницам.\n"
        "Нажми /quiz, чтобы сыграть! 😉"
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = weekday_nhatrang()
    chat_id = update.effective_chat.id

    # Воскресенье — выходной с напоминанием
    if today == REST_DAY:
        await update.message.reply_text(
            "🌙 Сегодня выходной от игры!\n\n"
            "Но у тебя есть важные задания на сегодня:\n\n"
            "📞 Позвони или напиши папе!\n"
            "❤️ Сделай несколько добрых дел.\n\n"
            "💰 Оплата за этот день сохраняется!\n\n"
            "Викторина вернётся в понедельник. Have a nice day! 😉"
        )
        return

    # Не игровой день (вт, чт, сб)
    if today not in PLAY_DAYS:
        await update.message.reply_text(
            "😴 Сегодня викторины нет.\n\n"
            "Игра выходит по понедельникам, средам и пятницам.\n"
            "Заходи в игровой день! 🎲"
        )
        return

    # Уже играла сегодня
    if already_played_today(chat_id):
        await update.message.reply_text(
            "✅ Ты уже играла сегодня!\n\n"
            "Приходи в следующий игровой день 😉"
        )
        return

    # Раздаём карты
    cards = CARDS.copy()
    random.shuffle(cards)
    context.chat_data["cards"] = cards

    keyboard = [
        [
            InlineKeyboardButton("🟥 1", callback_data="0"),
            InlineKeyboardButton("🟦 2", callback_data="1"),
            InlineKeyboardButton("🟩 3", callback_data="2")
        ],
        [
            InlineKeyboardButton("🟨 4", callback_data="3"),
            InlineKeyboardButton("🟪 5", callback_data="4")
        ]
    ]
    await update.message.reply_text(
        "🎲 СЕКРЕТНЫЕ КАРТЫ!\n\n"
        "Перед тобой 5 закрытых карт.\n"
        "Выбери ОДНУ наугад! 😈\n\n"
        "Что тебе сегодня выпадет?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def choose_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    cards = context.chat_data.get("cards")
    if not cards:
        await query.edit_message_text(
            "⚠️ Игра закончилась.\n\n"
            "Нажми /quiz в игровой день, чтобы начать новую."
        )
        return

    chosen = int(query.data)
    result = cards[chosen]

    context.chat_data.pop("cards", None)
    mark_played_today(update.effective_chat.id)

    await query.edit_message_text(
        f"🎉 ТЫ ВЫБРАЛА КАРТУ №{chosen + 1}!\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{result}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🎮 Игра окончена!\n"
        f"Следующая игра — в ближайший пн/ср/пт 😉"
    )


# --- Мини веб-сервер, чтобы Render не усыплял бота ---
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Бот работает!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)
# ----------------------------------------------------


def main():
    Thread(target=run_web).start()
    token = os.environ["BOT_TOKEN"]
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CallbackQueryHandler(choose_card, pattern="^[0-4]$"))
    app.run_polling()


if __name__ == "__main__":
    main()
