import os
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
CARDS = [
    "🎁 SURPRISE!\n+$3 к дневному заработку!",
    "💰 JACKPOT!\n×2 дневной заработок!\nБыло $7 → сегодня $14!",
    "😎 БЕЗ ИЗМЕНЕНИЙ\nОбычный день. Всё по плану.\n+$0",
    "🌴 EASY DAY!\nОдно из пяти заданий можно пропустить сегодня.",
    "❤️ ПАПИН ПОДАРОК!\n−$2 с папиного дневного счёта → дочке +$2!"
]
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Привет!\n\n"
        "Нажми /quiz, чтобы сыграть в секретную викторину!"
    )
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Случайно распределяем призы по пяти картам
    cards = CARDS.copy()
    random.shuffle(cards)
    # Сохраняем расположение призов для этой конкретной игры
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
            "Нажми /quiz, чтобы начать новую."
        )
        return
    chosen = int(query.data)
    result = cards[chosen]
    # Удаляем результат, чтобы нельзя было выбрать вторую карту
    context.chat_data.pop("cards", None)
    await query.edit_message_text(
        f"🎉 ТЫ ВЫБРАЛА КАРТУ №{chosen + 1}!\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{result}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🎮 Игра окончена!\n"
        f"Завтра — новая попытка 😉"
    )
def main():
    token = os.environ["BOT_TOKEN"]
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(
        CallbackQueryHandler(choose_card, pattern="^[0-4]$")
    )
    app.run_polling()
if __name__ == "__main__":
    main()
