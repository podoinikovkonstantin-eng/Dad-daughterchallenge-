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
    "🇳🇱 В Нидерландах велосипедов больше, чем жителей.",
    "🇧🇷 Через Бразилию протекает Амазонка — самая полноводная река планеты.",
    "🇮🇹 В Италии находится самое маленькое государство мира — Ватикан.",
    "🇨🇳 Великую Китайскую стену строили почти 2000 лет.",
    "🇫🇮 Финляндию называют «страной тысячи озёр» — их там около 188 тысяч.",
    "🇲🇽 В Мексике растёт кактус высотой с трёхэтажный дом.",
    "🇰🇷 В Южной Корее новорождённому иногда сразу считают «1 год».",
    "🇳🇴 В Норвегии летом солнце не заходит несколько недель подряд.",
    "🇵🇹 Португалия и Испания находятся на одном полуострове — Пиренейском.",
    "🇰🇪 В Кении есть озеро, которое из-за фламинго кажется розовым.",
    "🇨🇭 В Швейцарии нельзя держать одну морскую свинку — им нужна компания.",
    "🇮🇳 В Индии говорят на сотнях разных языков — больше, чем где-либо.",
    "🇸🇬 В Сингапуре запрещено жевать жвачку.",
    "🇹🇷 Турция расположена сразу в Европе и Азии.",
    "🇳🇿 В Новой Зеландии овец примерно в 5 раз больше, чем людей.",
    "🇮🇩 Индонезия состоит из более чем 17 000 островов.",
    "🇨🇱 В Чили есть пустыня Атакама — самое сухое место на Земле.",
    "🇲🇦 В Марокко есть город Шефшауэн, где почти все дома синие.",
    "🇵🇪 В Перу находится древний город инков Мачу-Пикчу высоко в горах.",
    "🇯🇴 В Иордании есть город Петра, вырезанный прямо в скалах.",
    "🦴 У новорождённого около 300 костей, а у взрослого — 206: часть срастается.",
    "🫀 Сердце бьётся примерно 100 000 раз в день.",
    "🧠 Мозг работает даже во сне — иногда активнее, чем днём.",
    "👅 Язык — самая сильная мышца относительно своего размера.",
    "🦷 Эмаль зубов — самая твёрдая ткань во всём теле.",
    "👁 Глаз различает около 10 миллионов оттенков цвета.",
    "💨 Чихание вылетает со скоростью около 160 км/ч.",
    "🩸 Все сосуды тела, вытянутые в линию, обогнули бы Землю дважды.",
    "🦵 Самая длинная кость в теле — бедренная.",
    "👂 Уши и нос растут всю жизнь — они не останавливаются.",
    "😴 Человек проводит во сне около трети всей жизни.",
    "🖐 Отпечатки пальцев уникальны — даже у близнецов они разные.",
    "🫁 За день человек делает около 20 000 вдохов.",
    "🦶 На ступне 26 костей — четверть всех костей тела в двух ногах.",
    "👀 Глаза моргают 15–20 раз в минуту — это миллионы раз в год.",
    "🦴 Самая маленькая кость тела — в ухе, размером с рисовое зёрнышко.",
    "🧠 Нервные сигналы бегут по телу со скоростью до 400 км/ч.",
    "💇 На голове в среднем около 100 000 волос.",
    "👃 Человек может различать около триллиона запахов.",
    "💧 Тело человека примерно на 60% состоит из воды.",
    "🪐 Кольца Сатурна состоят изо льда и камней — некоторые размером с дом.",
    "🌕 Следы астронавтов на Луне останутся миллионы лет — там нет ветра.",
    "☀️ Внутри Солнца поместился бы миллион таких планет, как Земля.",
    "🌟 Свет от Солнца летит до Земли около 8 минут.",
    "🔴 Марс красный из-за ржавчины — железа в его почве.",
    "🌌 В нашей галактике больше 100 миллиардов звёзд.",
    "🐙 У осьминога голубая кровь и девять «мозгов».",
    "🦒 У жирафа и у человека одинаковое число шейных позвонков — семь.",
    "🐬 Дельфины спят, отключая только половину мозга.",
    "🐌 Улитка может спать до трёх лет подряд.",
    "🦈 Акулы жили на Земле ещё до появления деревьев.",
    "🐧 Пингвины умеют выпрыгивать из воды почти на два метра.",
    "🌳 Деревья «общаются» через грибницу под землёй.",
    "🦋 Бабочка-монарх пролетает тысячи километров во время перелёта.",
    "🔢 Если сложить все числа от 1 до 100, получится ровно 5050.",
    "♾ Число «пи» бесконечно и никогда не повторяется.",
    "🍕 Пицца помогает понять дроби: 1/2, 1/4, 1/8 — это кусочки.",
    "🐝 Пчёлы строят соты шестиугольниками — самая экономная форма.",
    "🔺 Треугольник — самая прочная фигура, его используют в мостах.",
    "⚡ Молния горячее поверхности Солнца в несколько раз.",
    "🌈 Радуга на самом деле полный круг — с земли видно только её часть.",
    "🧊 Горячая вода иногда замерзает быстрее холодной (эффект Мпембы).",
    "🧲 Разрежь магнит пополам — у каждой половинки снова два полюса.",
    "📏 Миллион секунд — это 11 дней, а миллиард секунд — почти 32 года.",
    "🏅 США — лидер по Нобелевским премиям: более 400 лауреатов, у России и СССР — около 30.",
    "👮 В России около 525–643 полицейских на 100 000 человек, в США — примерно 250.",
    "📕 Самый высокий человек в истории был ростом 272 см.",
    "📕 Самая маленькая собака в мире помещается в ладонь.",
    "📕 Самая длинная кошка была длиннее метра.",
    "📕 Самое длинное научное слово содержит почти 190 000 букв.",
    "🇬🇧 Idiom: \"Piece of cake\" — something very easy to do.",
    "🇬🇧 Idiom: \"Break the ice\" — to start a conversation in a friendly way.",
    "🇬🇧 Idiom: \"Hit the books\" — to study hard.",
    "🇬🇧 Idiom: \"Under the weather\" — feeling a little sick.",
    "🇬🇧 Idiom: \"Once in a blue moon\" — something that happens very rarely.",
    "🇬🇧 Idiom: \"Spill the beans\" — to tell a secret.",
    "🇬🇧 Idiom: \"A bookworm\" — a person who loves reading.",
    "🇬🇧 Idiom: \"Butterflies in your stomach\" — feeling nervous or excited.",
    "🔤 ASAP — As Soon As Possible (как можно скорее).",
    "🔤 FYI — For Your Information (к твоему сведению).",
    "🔤 DIY — Do It Yourself (сделай сам).",
    "🔤 FAQ — Frequently Asked Questions (частые вопросы).",
    "🔤 IDK — I Don't Know (я не знаю).",
    "🔤 AKA — Also Known As (также известный как).",
    "🔤 BTW — By The Way (кстати).",
    "🔤 IMO — In My Opinion (по-моему).",
    "🇬🇧 Did you know? Honey never spoils.",
    "🇬🇧 Did you know? Octopuses have three hearts.",
    "🇬🇧 Did you know? A day on Venus is longer than its year.",
    "🇬🇧 Did you know? Bananas are berries, but strawberries are not.",
    "🇬🇧 Did you know? Butterflies taste with their feet.",
    "🇬🇧 Did you know? Sharks existed before trees."
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
    "🧮 Сколько будет 15% от 200?",
    "🧮 Если сейчас 14:45, сколько времени будет через 2 часа 30 минут?",
    "🧮 Найди 20% от 150.",
    "🧮 Магазин снизил цену $80 на 25%. Сколько стала цена?",
    "🧮 Посчитай: 12 × 12.",
    "🧮 Квадрат числа 15 — это сколько?",
    "🧮 Что больше: 2/3 или 3/5?",
    "🧮 Сократи дробь 12/18.",
    "🧮 На ферме куры и кролики: 8 голов и 22 ноги. Сколько кроликов?",
    "🧮 Карандаш дороже ручки на $2. Вместе $10. Сколько стоит ручка?",
    "🧮 Сколько прямоугольников в сетке 2×2 клетки?",
    "🧮 Периметр квадрата со стороной 7 см — это сколько?",
    "🧮 Площадь прямоугольника 6×4 см?",
    "🧮 Сколько градусов в сумме углов треугольника?",
    "🧮 Ты копишь по $6 в день. За сколько дней накопишь $150?",
    "🌍 Найди на карте страну на букву «М» и назови её столицу.",
    "🗺 Назови 5 стран Азии за одну минуту.",
    "🌎 Покажи на карте, где находится Вьетнам, и где — США.",
    "🏳 Вспомни флаг любой страны и нарисуй его по памяти.",
    "🧭 Назови 3 страны, где протекают самые длинные реки.",
    "🌐 Выбери страну, которую хочешь посетить, и назови 3 причины почему.",
    "🇬🇧 Say 5 animals in English out loud.",
    "🇬🇧 Describe your day in English in one sentence.",
    "🧩 Загадка: Идёт то в гору, то с горы, но остаётся на месте. Что это? Напиши в группу!",
    "🧩 Загадка: Что становится больше, если поставить его вверх ногами? Напиши в группу!",
    "🧩 Загадка: Что всегда впереди нас, но увидеть его нельзя? Напиши в группу!",
    "🧩 Загадка: Чем больше из неё берёшь, тем больше она становится. Что это? Напиши в группу!"
]

# ===== СУББОТА: задание папе (по /quiz) =====
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
    "🖊 Сочини четверостишие со словами: иголка, булка, нога, карга. Напиши в группу!",
    "🖊 Сочини четверостишие со словами: кошка, окошко, ложка, немножко. Напиши в группу!",
    "🖊 Сочини четверостишие со словами: тучка, ручка, штучка, закорючка. Напиши в группу!",
    "🖊 Сочини четверостишие со словами: банан, диван, туман, карман. Напиши в группу!",
    "🖊 Сочини четверостишие со словами: пингвин, апельсин, магазин, витамин. Напиши в группу!"
]

# ===== ЧЁРНЫЙ ЯЩИК (четверг, /box) =====
BLACK_BOX = [
    "👑 ТУЗ — $20! ДЖЕКПОТ!!! 🎉",
    "👸 ДАМА — $10! Крупный выигрыш!",
    "🤴 КОРОЛЬ — $3",
    "🎖 ВАЛЕТ — $2",
    "🔟 ДЕСЯТКА — $1,5",
    "9️⃣ ДЕВЯТКА — $1",
    "8️⃣ ВОСЬМЁРКА — $0,5",
    "😴 СЕМЁРКА — Ленивый день: одно задание сегодня можно не делать!",
    "📖 ШЕСТЁРКА — Сегодня достаточно читать 30 минут вместо 60 для 100%!",
    "🍀 ПЯТЁРКА — В этот раз без приза, но повезёт в другой раз!"
]

# ===== КАРТЫ УДАЧИ (вторник, /luck) =====
LUCK_CARDS = [
    "🛡 ИММУНИТЕТ НА НЕДЕЛЮ!\nДо 2 заданий можно перенести на другой день — с сохранением дневного заработка.",
    "😴 ЛЕНИВЫЙ ХУЛИБАМ!\n1 задание на этой неделе можно пропустить в любой день — с сохранением дневного заработка.",
    "💪 СУПЕР-СПОСОБНОСТЬ!\nВыполни 2 задания на 200% и более — получи по $1 сверху за каждое!",
    "🏆 ПРАВО ВЫБОРА!\nКакой пункт ты бы добавила в нашу игру? Напиши свою идею в группу!",
    "⭐ ОБЫЧНЫЙ ДЕНЬ.\nСегодня без бонуса, но ты всё равно молодец! 😊"
]

# ===== ТВОРЧЕСКИЙ КОНКУРС (суббота, /art) =====
ART_TASKS = [
    "🎨 Нарисуй рисунок на свободную тему и отправь фото в группу. (+$1)",
    "📸 Сделай необычное фото дня и отправь в группу. (+$1)",
    "🏷 Придумай название для следующей викторины и напиши в группу! (+$1)",
    "🎭 Нарисуй новую аватарку для Хулибам-бота и отправь в группу! (+$1)",
    "🖊 Сочини четверостишие на свободную тему и напиши в группу. (+$1)",
    "🤖 Сделай в нейросети забавное фото с папой (например, вы в виде животных) и отправь в группу. (+$1)"
]

# ===== Дни недели =====
PLAY_DAYS = [0, 2, 4]
FACT_DAY = 1
CHALLENGE_DAY = 3
SATURDAY = 5
REST_DAY = 6

# Лимиты
LIMIT_QUIZ = 1
LIMIT_FACT = 1
LIMIT_CHALLENGE = 1
LIMIT_SATURDAY = 1
LIMIT_BOX = 1
LIMIT_LUCK = 1
LIMIT_ART = 1

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


def get_count(chat_id, key):
    data = load_data()
    today = today_nhatrang().isoformat()
    rec = data.get(str(chat_id), {})
    if rec.get("date") == today:
        return rec.get(key, 0)
    return 0


def add_count(chat_id, key):
    data = load_data()
    today = today_nhatrang().isoformat()
    rec = data.get(str(chat_id), {})
    if rec.get("date") != today:
        rec = {"date": today}
    rec[key] = rec.get(key, 0) + 1
    data[str(chat_id)] = rec
    save_data(data)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Привет! Добро пожаловать в игру!\n\n"
        "📅 Твоя неделя:\n"
        "🎲 Пн, Ср, Пт — секретная викторина  →  /quiz\n"
        "💡 Вторник — «Знаешь ли ты?»  →  /quiz\n"
        "🍀 Вторник — Карты удачи  →  /luck\n"
        "🎯 Четверг — Колесо челленджей  →  /quiz\n"
        "🎁 Четверг — Чёрный ящик  →  /box\n"
        "✍️ Суббота — Задание для папы  →  /quiz\n"
        "🎨 Суббота — Творческий конкурс  →  /art\n"
        "🌙 Воскресенье — выходной\n\n"
        "Начни с /quiz!"
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = weekday_nhatrang()
    chat_id = update.effective_chat.id

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

    if today == FACT_DAY:
        if get_count(chat_id, "fact") >= LIMIT_FACT:
            await update.message.reply_text(
                "✅ Факт на сегодня ты уже узнала!\n\n"
                "Не забудь про Карты удачи — команда /luck 🍀"
            )
            return
        add_count(chat_id, "fact")
        fact = random.choice(FACTS)
        await update.message.reply_text(
            "💡 ЗНАЕШЬ ЛИ ТЫ?\n\n"
            f"{fact}\n\n"
            "Расскажи папе, если было интересно! 😊\n"
            "А ещё сегодня доступны Карты удачи — /luck 🍀"
        )
        return

    if today == CHALLENGE_DAY:
        if get_count(chat_id, "challenge") >= LIMIT_CHALLENGE:
            await update.message.reply_text(
                "✅ Челлендж на сегодня ты уже получила!\n\n"
                "Не забудь открыть Чёрный ящик — команда /box 🎁"
            )
            return
        keyboard = [[InlineKeyboardButton("🎯 КРУТИТЬ!", callback_data="spin")]]
        await update.message.reply_text(
            "🎯 КОЛЕСО ЧЕЛЛЕНДЖЕЙ!\n\n"
            "Нажми кнопку и получи случайный челлендж!\n"
            "А потом открой Чёрный ящик — /box 🎁",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if today == SATURDAY:
        if get_count(chat_id, "saturday") >= LIMIT_SATURDAY:
            await update.message.reply_text(
                "✅ Задание на сегодня ты уже получила!\n\n"
                "А ещё сегодня творческий конкурс — команда /art 🎨"
            )
            return
        add_count(chat_id, "saturday")
        task = random.choice(SATURDAY_TASKS)
        await update.message.reply_text(
            "✍️ ЗАДАНИЕ ДНЯ!\n\n"
            f"{task}\n\n"
            "А ещё сегодня творческий конкурс за $1 — /art 🎨"
        )
        return

    if today in PLAY_DAYS:
        if get_count(chat_id, "quiz") >= LIMIT_QUIZ:
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
    add_count(update.effective_chat.id, "quiz")

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

    if get_count(chat_id, "challenge") >= LIMIT_CHALLENGE:
        await query.edit_message_text(
            "✅ Челлендж на сегодня ты уже получила!\n\n"
            "Не забудь про Чёрный ящик — /box 🎁"
        )
        return

    add_count(chat_id, "challenge")
    challenge = random.choice(CHALLENGES)
    await query.edit_message_text(
        "🎯 ТВОЙ ЧЕЛЛЕНДЖ:\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{challenge}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        "Справишься? 💪 А теперь открой Чёрный ящик — /box 🎁"
    )


async def box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = weekday_nhatrang()
    chat_id = update.effective_chat.id

    if today != CHALLENGE_DAY:
        await update.message.reply_text(
            "🎁 Чёрный ящик открывается только по четвергам!\n\n"
            "Загляни в четверг 😉"
        )
        return

    if get_count(chat_id, "box") >= LIMIT_BOX:
        await update.message.reply_text(
            "✅ Ты уже открывала Чёрный ящик сегодня!\n\n"
            "Приходи в следующий четверг 🎁"
        )
        return

    boxes = BLACK_BOX.copy()
    random.shuffle(boxes)
    context.chat_data["boxes"] = boxes

   keyboard = [
        [
            InlineKeyboardButton("1 🃏", callback_data="box_0"),
            InlineKeyboardButton("2 🃏", callback_data="box_1"),
            InlineKeyboardButton("3 🃏", callback_data="box_2"),
            InlineKeyboardButton("4 🃏", callback_data="box_3"),
            InlineKeyboardButton("5 🃏", callback_data="box_4")
        ],
        [
            InlineKeyboardButton("6 🃏", callback_data="box_5"),
            InlineKeyboardButton("7 🃏", callback_data="box_6"),
            InlineKeyboardButton("8 🃏", callback_data="box_7"),
            InlineKeyboardButton("9 🃏", callback_data="box_8"),
            InlineKeyboardButton("10 🃏", callback_data="box_9")
        ]
    ]
    await update.message.reply_text(
        "🎁 ЧЁРНЫЙ ЯЩИК!\n\n"
        "Перед тобой 10 закрытых карт.\n"
        "Выбери ОДНУ — что внутри? 😈\n\n"
        "💰 Там могут быть $20, $10 и другие призы!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def choose_box(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    boxes = context.chat_data.get("boxes")
    if not boxes:
        await query.edit_message_text(
            "⚠️ Ящик уже закрыт.\n\n"
            "Открой новый командой /box в четверг."
        )
        return

    chosen = int(query.data.replace("box_", ""))
    result = boxes[chosen]

    context.chat_data.pop("boxes", None)
    add_count(update.effective_chat.id, "box")

    await query.edit_message_text(
        f"🎁 ТЫ ОТКРЫЛА КАРТУ №{chosen + 1}!\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{result}\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"Следующий ящик — в четверг! 🎉"
    )


async def luck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = weekday_nhatrang()
    chat_id = update.effective_chat.id

    if today != FACT_DAY:
        await update.message.reply_text(
            "🍀 Карты удачи открываются только по вторникам!\n\n"
            "Загляни во вторник 😉"
        )
        return

    if get_count(chat_id, "luck") >= LIMIT_LUCK:
        await update.message.reply_text(
            "✅ Карту удачи ты уже вытянула сегодня!\n\n"
            "Приходи в следующий вторник 🍀"
        )
        return

    add_count(chat_id, "luck")
    card = random.choice(LUCK_CARDS)
    await update.message.reply_text(
        "🍀 КАРТА УДАЧИ!\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{card}\n\n"
        f"━━━━━━━━━━━━━━"
    )


async def art(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = weekday_nhatrang()
    chat_id = update.effective_chat.id

    if today != SATURDAY:
        await update.message.reply_text(
            "🎨 Творческий конкурс проходит только по субботам!\n\n"
            "Загляни в субботу 😉"
        )
        return

    if get_count(chat_id, "art") >= LIMIT_ART:
        await update.message.reply_text(
            "✅ Творческое задание ты уже получила сегодня!\n\n"
            "Выполни его и отправь в группу 🎨"
        )
        return

    add_count(chat_id, "art")
    task = random.choice(ART_TASKS)
    await update.message.reply_text(
        "🎨 ТВОРЧЕСКИЙ КОНКУРС — $1!\n\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"{task}\n\n"
        f"━━━━━━━━━━━━━━"
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
    app.add_handler(CommandHandler("box", box))
    app.add_handler(CommandHandler("luck", luck))
    app.add_handler(CommandHandler("art", art))
    app.add_handler(CallbackQueryHandler(choose_card, pattern="^[0-4]$"))
    app.add_handler(CallbackQueryHandler(spin_wheel, pattern="^spin$"))
    app.add_handler(CallbackQueryHandler(choose_box, pattern="^box_[0-9]$"))
    app.run_polling()


if __name__ == "__main__":
    main()
