import os
import random
import json
import datetime
from zoneinfo import ZoneInfo
from threading import Thread
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== ВИКТОРИНА (пн/ср/пт) =====
CARDS = [
    "🎁 SURPRISE!\n+$3 к дневному заработку!",
    "💰 JACKPOT!\n×2 дневной заработок!\nБыло $7 → сегодня $14!",
    "😎 БЕЗ ИЗМЕНЕНИЙ\nОбычный день. Всё по плану.\n+$0",
    "🌴 EASY DAY!\nОдно из пяти заданий можно пропустить сегодня.",
    "❤️ ПАПИН ПОДАРОК!\n−$2 с папиного дневного счёта → дочке +$2!"
]

# ===== ВТОРНИК: «Знаешь ли ты?» =====
FACTS = [
    "🇯🇵 В Японии есть остров Окуносима, где живут сотни диких кроликов.",
    "🇷🇺 Россия — самая большая страна мира, она граничит с 14 странами.",
    "🇻🇳 Вьетнам — второй в мире экспортёр кофе после Бразилии.",
    "🇮🇸 В Исландии нет комаров — вообще ни одного.",
    "🇦🇺 В Австралии кенгуру и эму больше, чем людей в некоторых регионах.",
    "🇨🇦 В Канаде больше озёр, чем во всех остальных странах мира вместе взятых.",
    "🇪🇬 Древние египтяне изобрели зубную пасту более 5000 лет назад.",
    "🇳🇱 В Нидерландах так много велосипедов, что их больше, чем жителей.",
    "🇧🇷 Через Бразилию протекает Амазонка — самая полноводная река планеты.",
    "🇮🇹 В Италии находится самое маленькое государство мира — Ватикан.",
    "🇨🇳 Великую Китайскую стену строили почти 2000 лет.",
    "🇫🇮 Финляндию называют «страной тысячи озёр» — их там около 188 тысяч.",
    "🇲🇽 В Мексике растёт кактус высотой с трёхэтажный дом.",
    "🇰🇷 В Южной Корее возраст иногда считают иначе: новорождённому уже «1 год».",
    "🇳🇴 В Норвегии летом солнце не заходит несколько недель подряд.",
    "🇵🇹 Португалия и Испания находятся на одном полуострове — Пиренейском.",
    "🇰🇪 В Кении находится озеро, которое из-за фламинго кажется розовым.",
    "🇨🇭 В Швейцарии есть закон: нельзя держать одну морскую свинку — им нужна компания.",
    "🇮🇳 В Индии говорят на сотнях разных языков — больше, чем где-либо.",
    "🦴 У новорождённого около 300 костей, а у взрослого — всего 206: часть срастается.",
    "🫀 Сердце бьётся примерно 100 000 раз в день.",
    "🧠 Мозг работает даже во сне — иногда активнее, чем днём.",
    "👅 Язык — самая сильная мышца относительно своего размера.",
    "🦷 Эмаль зубов — самая твёрдая ткань во всём теле.",
    "👁 Глаз может различать около 10 миллионов оттенков цвета.",
    "💨 Чихание вылетает со скоростью около 160 км/ч.",
    "🩸 Все сосуды тела, вытянутые в линию, обогнули бы Землю дважды.",
    "🦵 Самая длинная кость в теле — бедренная.",
    "👂 Уши и нос растут всю жизнь, они не останавливаются.",
    "😴 Человек проводит во сне около трети всей жизни.",
    "🖐 Отпечатки пальцев уникальны — даже у близнецов они разные.",
    "🧬 В теле человека триллионы клеток, и почти все обновляются со временем.",
    "🫁 За день человек делает около 20 000 вдохов.",
    "🦶 На ступне 26 костей — это четверть всех костей тела в двух ногах.",
    "➗ Ноль придумали позже других цифр — древние люди обходились без него.",
    "🔢 Если сложить все числа от 1 до 100, получится ровно 5050.",
    "♾ Число «пи» бесконечно и никогда не повторяется — его считают до триллионов знаков.",
    "🍕 Пицца помогает объяснить дроби: 1/2, 1/4, 1/8 — это кусочки.",
    "🐝 Пчёлы строят соты шестиугольниками — это самая экономная форма.",
    "🔺 Треугольник — самая прочная фигура, поэтому его используют в мостах.",
    "🇬🇧 Did you know? A group of flamingos is called a \"flamboyance\". (Стая фламинго называется «фламбуайанс».)",
    "🇬🇧 Did you know? Honey never spoils. (Мёд никогда не портится.)",
    "🇬🇧 Did you know? Octopuses have three hearts. (У осьминога три сердца.)",
    "🇬🇧 Did you know? A day on Venus is longer than its year. (День на Венере длиннее её года.)",
    "🇬🇧 Did you know? Bananas are berries, but strawberries are not. (Бананы — ягоды, а клубника — нет.)",
    "🇬🇧 Did you know? The Eiffel Tower can be 15 cm taller in summer. (Летом Эйфелева башня выше на 15 см.)",
    "🇬🇧 Did you know? Butterflies taste with their feet. (Бабочки чувствуют вкус лапками.)",
    "🇬🇧 Did you know? There are more stars than grains of sand on Earth. (Звёзд больше, чем песчинок на Земле.)"
]

# ===== ЧЕТВЕРГ: колесо челленджей =====
CHALLENGES = [
    "💧 Выпей стакан воды прямо сейчас.",
    "🤸 Сделай 15 прыжков.",
    "🧘 Постой на одной ноге 30 секунд, потом на другой.",
    "🏃 Пробегись на месте, пока считаешь до 60.",
    "🙆 Сделай 10 наклонов и потянись к небу.",
    "🚶 Пройди 20 шагов на носочках.",
    "💪 Сделай 5 отжиманий (можно от стены).",
    "🧮 Посчитай в уме: 17 × 6.",
    "🧮 Сколько будет 144 : 12?",
    "🧮 Реши: 25 + 38 + 12.",
    "🧮 Сколько минут в 3 с половиной часах?",
    "🧮 Задумай число, умножь на 2, прибавь 10, раздели на 2, отними задуманное. Получилось 5? 😉",
    "🧮 Сколько будет 15% от 200?",
    "🧮 Если сейчас 14:45, сколько времени будет через 2 часа 30 минут?",
    "🌍 Найди на карте страну на букву «М» и назови её столицу.",
    "🗺 Назови 5 стран Азии за одну минуту.",
    "🌎 Покажи на карте, где находится Вьетнам, и где — США.",
    "🏳 Вспомни флаг любой страны и нарисуй его по памяти.",
    "🧭 Назови 3 страны, где протекают самые длинные реки.",
    "🌐 Выбери страну, которую хочешь посетить, и назови 3 причины почему.",
    "🇬🇧 Say 5 animals in English out loud. (Назови 5 животных по-английски вслух.)",
    "🇬🇧 Describe your day in English in one sentence. (Опиши свой день по-английски.)",
    "🧩 Загадка: Что можно увидеть с закрытыми глазами? Напиши ответ в группу!",
    "🧩 Загадка: Идёт то в гору, то с горы, но остаётся на месте. Что это? Напиши в группу!",
    "🧩 Загадка: Что становится больше, если поставить его вверх ногами? Напиши в группу!",
    "🧩 Загадка: Что всегда впереди нас, но увидеть его нельзя? Напиши в группу!",
    "🧩 Загадка: Чем больше из неё берёшь, тем больше она становится. Что это? Напиши в группу!"
]

# ===== СУББОТА: «Расскажи папе» + творчество =====
SATURDAY_TASKS = [
    "✍️ Напиши папе 2 предложения: о чём был вчерашний рассказ, который ты читала?",
    "📚 Расскажи папе в двух предложениях, какие новые слова ты выучила на этой неделе.",
    "🌍 Напиши папе: какую страну ты недавно узнала и что в ней интересного?",
    "💭 Напиши папе 2 предложения о том, чем ты гордишься на этой неделе.",
    "📖 Какую книгу ты сейчас читаешь? Опиши папе главного героя в двух предложениях.",
    "⭐ Расскажи папе об одном новом, что ты узнала за неделю.",
    "🎨 Напиши папе, что интересного ты нарисовала или сделала своими руками.",
    "✍️ Write dad 2 sentences in English about your favorite food.",
    "🇬🇧 Tell dad in English: what is your favorite country and why?",
    "✏️ Нарисуй что-нибудь за 5 минут и отправь фото в группу.",
    "🎵 Придумай короткую песенку из 4 строчек и спой папе.",
    "🎨 Нарисуй своё настроение цветом и отправь фото в группу.",
    "⭐ Сделай одно доброе дело, о котором никто не просил.",
    "🖊 Сочини четверостишие со словами: иголка, булка, нога, карга. Напиши в группу!",
    "🖊 Сочини четверостишие со словами: кошка, окошко, ложка, немножко. Напиши в группу!",
    "🖊 Сочини четверостишие со словами: тучка, ручка, штучка, закорючка. Напиши в группу!",
    "🖊 Сочини четверостишие со словами: банан, диван, туман, карман. Напиши в группу!",
    "🖊 Сочини четверостишие со словами: пингвин, апельсин, магазин, витамин. Напиши в группу!"
]

# ===== Дни недели =====
PLAY_DAYS = [0, 2, 4]   # викторина: пн, ср, пт
FACT_DAY = 1            # вторник
CHALLENGE_DAY = 3       # четверг
SATURDAY = 5            # суббота
REST_DAY = 6            # воскресенье

# Лимиты попыток в день
LIMIT_QUIZ = 1       # викторина (пн/ср/пт)
LIMIT_FACT = 2       # вторник
LIMIT_CHALLENGE = 2  # четверг (прокруты колеса)
LIMIT_SATURDAY = 1   # суббота

# Часовой пояс Нячанга (Вьетнам). Игра идёт по времени дочери.
NHATRANG = ZoneInfo("Asia/Ho_Chi_Minh")

PLAYED_FILE = "played.json"


def today_nhatrang():
    return datetime.datetime.now(NHATRANG).date()


def weekday_nhatrang():
    return today_nhatrang().weekday()


def load_data():
    try:
        with open(PLAYED_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_data(data):
    with open(PLAYED_FILE, "w") as f:
        json.dump(data, f)


def get_count(chat_id):
    """Сколько раз этот чат уже играл сегодня."""
    data = load_data()
    today = today_nhatrang().isoformat()
    rec = data.get(str(chat_id))
    if rec and rec.get("date") == today:
        return rec.get("count", 0)
    return 0


def add_count(chat_id):
    """Увеличить счётчик попыток на сегодня."""
    data = load_data()
    today = today_nhatrang().isoformat()
    rec = data.get(str(chat_id))
    if rec and rec.get("date") == today:
        rec["count"] = rec.get("count", 0) + 1
    else:
        data[str(chat_id)] = {"date": today, "count": 1}
    save_data(data)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Привет!\n\n"
        "Каждый день тебя ждёт что-то новое:\n"
        "🎲 Пн, Ср, Пт — секретная викторина\n"
        "💡 Вторник — «Знаешь ли ты?»\n"
        "🎯 Четверг — колесо челленджей\n"
        "✍️ Суббота — задание для папы\n"
        "🌙 Воскресенье — выходной\n\n"
        "Нажми /quiz, чтобы узнать задание на сегодня!"
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = weekday_nhatrang()
    chat_id = update.effective_chat.id

    # Воскресенье — выходной
    if today == REST_DAY:
        await update.message.reply_text(
            "🌙 Сегодня выходной от игры!\n\n"
            "Но у тебя есть важные задания на сегодня:\n\n"
            "📞 Позвони папе!\n"
            "❤️ Сделай несколько добрых дел.\n\n"
            "💰 Оплата за день сохраняется!\n\n"
            "Викторина вернётся в понедельник 😉"
        )
        return

    # Вторник — 2 факта в день
    if today == FACT_DAY:
        if get_count(chat_id) >= LIMIT_FACT:
            await update.message.reply_text(
                "✅ На сегодня хватит фактов!\n\n"
                "Приходи завтра за новыми знаниями 😉"
            )
            return
        add_count(chat_id)
        fact = random.choice(FACTS)
        await update.message.reply_text(
            "💡 ЗНАЕШЬ ЛИ ТЫ?\n\n"
            f"{fact}\n\n"
            "Расскажи папе, если было интересно! 😊"
        )
        return

    # Четверг — колесо (2 прокрута в день, лимит проверяем при нажатии кнопки)
    if today == CHALLENGE_DAY:
        if get_count(chat_id) >= LIMIT_CHALLENGE:
            await update.message.reply_text(
                "✅ Ты уже прокрутила колесо 2 раза сегодня!\n\n"
                "Приходи завтра 😉"
            )
            return
        keyboard = [[InlineKeyboardButton("🎯 КРУТИТЬ!", callback_data="spin")]]
        await update.message.reply_text(
            "🎯 КОЛЕСО ЧЕЛЛЕНДЖЕЙ!\n\n"
            "Нажми кнопку и получи случайный челлендж на сегодня!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Суббота — 1 задание в день
    if today == SATURDAY:
        if get_count(chat_id) >= LIMIT_SATURDAY:
            await update.message.reply_text(
                "✅ Задание на сегодня ты уже получила!\n\n"
                "Выполни его для папы 😊"
            )
            return
        add_count(chat_id)
        task = random.choice(SATURDAY_TASKS)
        await update.message.reply_text(
            "✍️ ЗАДАНИЕ ДНЯ!\n\n"
            f"{task}"
        )
        return

    # Пн/Ср/Пт — викторина, 1 раз в день
    if today in PLAY_DAYS:
        if get_count(chat_id) >= LIMIT_QUIZ:
            await update.message.reply_text(
                "✅ Ты уже играла сегодня!\n\n"
                "Приходи в следующий игровой день 😉"
            )
            return

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
    add_count(update.effective_chat.id)

    await query.edit_message_text(
        f"🎉 ТЫ ВЫБРАЛА КАРТУ №{chosen + 1}!\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{result}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"🎮 Игра окончена!\n"
        f"Следующая игра — в ближайший пн/ср/пт 😉"
    )


async def spin_wheel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id

    # Проверяем лимит прокрутов в момент нажатия
    if get_count(chat_id) >= LIMIT_CHALLENGE:
        await query.edit_message_text(
            "✅ Ты уже прокрутила колесо 2 раза сегодня!\n\n"
            "Приходи завтра 😉"
        )
        return

    add_count(chat_id)
    challenge = random.choice(CHALLENGES)
    await query.edit_message_text(
        "🎯 ТВОЙ ЧЕЛЛЕНДЖ:\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{challenge}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        "Справишься? 💪"
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
    app.add_handler(CallbackQueryHandler(spin_wheel, pattern="^spin$"))
    app.run_polling()


if __name__ == "__main__":
    main()
