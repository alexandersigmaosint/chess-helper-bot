import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ВСТАВЬ СЮДА СВОЙ ТОКЕН ОТ @BotFather (или задай через переменные окружения на хостинге)
BOT_TOKEN = os.getenv("9097032667:AAEJwMHzMi1AompKo4WTM4J7ub1hbXSM89M", "9097032667:AAEJwMHzMi1AompKo4WTM4J7ub1hbXSM89M")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище выбранного языка пользователей (по умолчанию 'ru')
user_lang = {}

# Словарь всех текстов и кнопок на двух языках
TEXTS = {
    "ru": {
        "welcome": "Я Chess Cheats Helper, чем могу помочь?",
        "btn_connect": "🔌 Как подключить Чит?",
        "btn_ban": "🛡 За это банят?",
        "btn_broken": "🛠 Чит не работает",
        "btn_change_lang": "🌐 Сменить язык",
        "btn_back_main": "⬅️ В главное меню",
        "btn_back_os": "⬅️ К выбору ОС",
        "choose_os": "Выберите вашу операционную систему:",
        "choose_cheat_android": "Выберите чит для Android:",
        "choose_cheat_pc": "Выберите чит для ПК:",
        "inst_mobile": (
            "📱 <b>Инструкция по установке:</b>\n\n"
            "1) Скачай приложение\n"
            "2) Открой его\n"
            "3) Зарегистрируйся\n"
            "4) Играй"
        ),
        "inst_chesslens": (
            "🖥 <b>Инструкция для ChessLens:</b>\n\n"
            "1. Распакуйте этот ZIP-архив в обычную папку.\n"
            "2. Установите Python 3.10+; во время установки обязательно выберите опцию <b>Add Python to PATH</b>.\n"
            "3. Запустите файл <code>install_dependencies.bat</code> (двойным щелчком) и дождитесь завершения процесса.\n"
            "4. Запустите файл <code>launch.bat</code> (двойным щелчком)."
        ),
        "inst_chesscoach": (
            "🌐 <b>Инструкция для ChessCoach (Расширение):</b>\n\n"
            "1. Скачайте или клонируйте проект.\n"
            "2. Откройте <code>chrome://extensions/</code>.\n"
            "3. Включите режим разработчика.\n"
            "4. Нажмите <code>Загрузить распакованное расширение</code>.\n"
            "5. Выберите каталог проекта, в котором находится <code>manifest.json</code>.\n"
            "6. Перезагрузите уже открытые вкладки Lichess и Chess.com."
        ),
        "ban_info": (
            "🛡 <b>Информация о банах:</b>\n\n"
            "За ChessCoach — <b>Нет</b>\n"
            "За ChessPilot — <b>Могут</b>\n"
            "За ChessLens — <b>Могут</b>"
        ),
        "support_info": "🛠 Обращайтесь в поддержку к @mhcheat"
    },
    "en": {
        "welcome": "I am Chess Cheats Helper, how can I help you?",
        "btn_connect": "🔌 How to connect the Cheat?",
        "btn_ban": "🛡 Can I get banned?",
        "btn_broken": "🛠 Cheat is not working",
        "btn_change_lang": "🌐 Change Language",
        "btn_back_main": "⬅️ Main Menu",
        "btn_back_os": "⬅️ Back to OS",
        "choose_os": "Select your operating system:",
        "choose_cheat_android": "Select a cheat for Android:",
        "choose_cheat_pc": "Select a cheat for PC:",
        "inst_mobile": (
            "📱 <b>Installation Guide:</b>\n\n"
            "1) Download the app\n"
            "2) Open it\n"
            "3) Register\n"
            "4) Play"
        ),
        "inst_chesslens": (
            "🖥 <b>ChessLens Guide:</b>\n\n"
            "1. Extract this ZIP archive into a regular folder.\n"
            "2. Install Python 3.10+; during installation, make sure to check <b>Add Python to PATH</b>.\n"
            "3. Run <code>install_dependencies.bat</code> (double-click) and wait for it to finish.\n"
            "4. Run <code>launch.bat</code> (double-click)."
        ),
        "inst_chesscoach": (
            "🌐 <b>ChessCoach Guide (Extension):</b>\n\n"
            "1. Download or clone the project.\n"
            "2. Open <code>chrome://extensions/</code>.\n"
            "3. Enable Developer Mode.\n"
            "4. Click <code>Load unpacked</code>.\n"
            "5. Select the project directory containing <code>manifest.json</code>.\n"
            "6. Reload already open Lichess and Chess.com tabs."
        ),
        "ban_info": (
            "🛡 <b>Ban Risk Information:</b>\n\n"
            "For ChessCoach — <b>No</b>\n"
            "For ChessPilot — <b>Possible</b>\n"
            "For ChessLens — <b>Possible</b>"
        ),
        "support_info": "🛠 Contact support at @mhcheat"
    }
}

# --- КЛАВИАТУРЫ ---

def kb_language():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]
    ])

def kb_main(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_connect"], callback_data="menu_connect")],
        [InlineKeyboardButton(text=t["btn_ban"], callback_data="menu_ban")],
        [InlineKeyboardButton(text=t["btn_broken"], callback_data="menu_broken")],
        [InlineKeyboardButton(text=t["btn_change_lang"], callback_data="change_lang")]
    ])

def kb_os(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Android", callback_data="os_android")],
        [
            InlineKeyboardButton(text="🪟 Windows", callback_data="os_pc"),
            InlineKeyboardButton(text="🍎 MacOS", callback_data="os_pc"),
            InlineKeyboardButton(text="🐧 Linux", callback_data="os_pc")
        ],
        [InlineKeyboardButton(text=t["btn_back_main"], callback_data="back_main")]
    ])

def kb_cheats_android(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ChessPilot", callback_data="cheat_mobile"),
            InlineKeyboardButton(text="ChessCoach", callback_data="cheat_mobile")
        ],
        [InlineKeyboardButton(text=t["btn_back_os"], callback_data="menu_connect")]
    ])

def kb_cheats_pc(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ChessLens", callback_data="cheat_chesslens"),
            InlineKeyboardButton(text="ChessCoach", callback_data="cheat_chesscoach")
        ],
        [InlineKeyboardButton(text=t["btn_back_os"], callback_data="menu_connect")]
    ])

def kb_back_main(lang: str):
    t = TEXTS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["btn_back_main"], callback_data="back_main")]
    ])

# --- ОБРАБОТЧИКИ ---

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Выберите язык / Choose language:",
        reply_markup=kb_language()
    )

@dp.callback_query(F.data == "change_lang")
async def cb_change_lang(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите язык / Choose language:",
        reply_markup=kb_language()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("lang_"))
async def cb_set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    user_lang[callback.from_user.id] = lang
    await callback.message.edit_text(
        TEXTS[lang]["welcome"],
        reply_markup=kb_main(lang)
    )
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def cb_back_main(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.edit_text(
        TEXTS[lang]["welcome"],
        reply_markup=kb_main(lang)
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_connect")
async def cb_menu_connect(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.edit_text(
        TEXTS[lang]["choose_os"],
        reply_markup=kb_os(lang)
    )
    await callback.answer()

@dp.callback_query(F.data == "os_android")
async def cb_os_android(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.edit_text(
        TEXTS[lang]["choose_cheat_android"],
        reply_markup=kb_cheats_android(lang)
    )
    await callback.answer()

@dp.callback_query(F.data == "os_pc")
async def cb_os_pc(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.edit_text(
        TEXTS[lang]["choose_cheat_pc"],
        reply_markup=kb_cheats_pc(lang)
    )
    await callback.answer()

@dp.callback_query(F.data == "cheat_mobile")
async def cb_cheat_mobile(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.edit_text(
        TEXTS[lang]["inst_mobile"],
        reply_markup=kb_back_main(lang),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "cheat_chesslens")
async def cb_cheat_chesslens(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.edit_text(
        TEXTS[lang]["inst_chesslens"],
        reply_markup=kb_back_main(lang),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "cheat_chesscoach")
async def cb_cheat_chesscoach(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.edit_text(
        TEXTS[lang]["inst_chesscoach"],
        reply_markup=kb_back_main(lang),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_ban")
async def cb_menu_ban(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.edit_text(
        TEXTS[lang]["ban_info"],
        reply_markup=kb_back_main(lang),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_broken")
async def cb_menu_broken(callback: CallbackQuery):
    lang = user_lang.get(callback.from_user.id, "ru")
    await callback.message.edit_text(
        TEXTS[lang]["support_info"],
        reply_markup=kb_back_main(lang)
    )
    await callback.answer()

# --- ВЕБ-СЕРВЕР ДЛЯ РАБОТЫ 24/7 НА ХОСТИНГЕ (RENDER.COM / RAILWAY) ---

async def handle_ping(request):
    return web.Response(text="Chess Cheats Helper Bot is running 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
