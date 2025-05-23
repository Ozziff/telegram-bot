#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram bot implementation for a beer selection bot.
Includes text responses and image sending capabilities.
"""

import os
import logging
import random
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Set higher logging level for httpx to avoid excessive logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Get token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
if not BOT_TOKEN:
    logger.error("Bot token not found. Please set the BOT_TOKEN environment variable.")
    exit(1)

# Simple web server to keep Render happy
def run_web_server():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Pivnoi Vopros Bot is running!')
            
        def log_message(self, format, *args):
            # Suppress log messages to console
            return
    
    # Use the PORT environment variable that Render sets
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    logger.info(f"Starting web server on port {port}")
    server.serve_forever()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    keyboard = [[InlineKeyboardButton("Испытай удачу, сталкер", callback_data="try_luck")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Привет, сталкер. Замотался? Присядь, выпей кружечку холодненького. Сейчас сделаем тебе случайную подборку из 6 зелий.",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    help_text = (
        "Вот команды, которые я понимаю:\n"
        "/start - Начать разговор\n"
        "/help - Показать это сообщение\n"
        "/menu - Показать меню опций\n\n"
        "Также вы можете просто написать ваш вопрос о пиве, и я постараюсь ответить!"
    )
    await update.message.reply_text(help_text)

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display a menu of options with inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("История пива", callback_data="history"),
            InlineKeyboardButton("Виды пива", callback_data="types")
        ],
        [
            InlineKeyboardButton("Процесс варки", callback_data="brewing"),
            InlineKeyboardButton("Культура пития", callback_data="culture")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите тему, которая вас интересует:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses from inline keyboard."""
    query = update.callback_query
    await query.answer()

    if query.data == "try_luck":
        # List of beers
        beers = ["Крушовица", "Жатецкий гусь", "Хамовники венское", 
                 "Хамовники пильзенское", "Козел"]
        
        # Randomly select beers with 30% chance of Жигули барное
        selected_beers = []
        for _ in range(6):
            if random.random() < 0.3:  # 30% chance for Жигули барное
                selected_beers.append("Жигули барное")
            else:
                selected_beers.append(random.choice(beers))
        
        # Count how many "Жигули барное" we have
        zhiguli_count = selected_beers.count("Жигули барное")
        
        # Create a formatted message
        beer_message = "Твой выбор, сталкер 🍺:\n\n"
        for i, beer in enumerate(selected_beers, 1):
            beer_message += f"{i}. {beer}\n"
        
        beer_message += "\nНе дай Зоне себя победить! ☢️"
        
        # First send the text message
        await query.edit_message_text(text=beer_message)
        
        # Then send appropriate image based on Zhiguli count
        chat_id = query.message.chat_id
        if zhiguli_count >= 3:
            # Send happy Zhiguli image
            with open('zhiguli_happy.png', 'rb') as photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo)
        else:
            # Send sad Zhiguli image
            with open('zhiguli_sad.png', 'rb') as photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo)
        
        return

    # Map callback data to text responses for other buttons
    responses = {
        "history": "История пива насчитывает тысячи лет. Первые упоминания о пивоварении относятся к древним цивилизациям Месопотамии и Египта. Пиво было важным продуктом питания и частью культуры многих народов.",
        
        "types": "Основные виды пива:\n- Эль (верховое брожение)\n- Лагер (низовое брожение)\n- Портер и стаут\n- Пшеничное пиво\n- IPA (India Pale Ale)\n- Ламбик (спонтанное брожение)\nКаждый вид имеет свои особенности вкуса, аромата и технологии производства.",
        
        "brewing": "Основные этапы пивоварения:\n1. Соложение зерна\n2. Затирание и фильтрация\n3. Варка сусла с хмелем\n4. Охлаждение сусла\n5. Ферментация (брожение)\n6. Созревание пива\n7. Фильтрация и розлив\nКаждый этап критически важен для качества готового продукта.",
        
        "culture": "Культура потребления пива различается по странам. В Германии традиционны пивные фестивали, такие как Октоберфест. В Бельгии каждый сорт пива подается в специальном бокале. В Чехии пиво - национальное достояние. Ответственное потребление и знание традиций обогащает опыт наслаждения этим напитком."
    }

    # Send the appropriate text response based on callback data
    if query.data in responses:
        await query.edit_message_text(text=responses[query.data])
    else:
        await query.edit_message_text(text="Извините, информация по этой теме временно недоступна.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages from users."""
    text = update.message.text.lower()
    
    # Simple keyword-based responses
    if "привет" in text or "здравствуй" in text:
        await update.message.reply_text("Привет! Чем могу помочь?")
    
    elif any(word in text for word in ["спасибо", "благодар"]):
        await update.message.reply_text("Всегда рад помочь!")
    
    elif any(word in text for word in ["пока", "до свидания"]):
        await update.message.reply_text("До новых встреч! Надеюсь, был полезен.")
    
    # Beer related questions
    elif "ipa" in text or "ипа" in text:
        await update.message.reply_text(
            "India Pale Ale (IPA) - это сорт пива с ярко выраженным хмелевым вкусом и ароматом. "
            "Первоначально был создан для экспорта в Индию, отсюда и название. "
            "Характеризуется высоким содержанием хмеля, который использовался как консервант."
        )
    
    elif "лагер" in text:
        await update.message.reply_text(
            "Лагер - это пиво низового брожения, которое выдерживается при низких температурах. "
            "Процесс ферментации происходит в нижней части чана, отсюда и название 'низовое'. "
            "Лагеры обычно более легкие и освежающие, чем эли."
        )
    
    elif "эль" in text:
        await update.message.reply_text(
            "Эль - это пиво верхового брожения. Процесс ферментации происходит при более высоких температурах, "
            "чем у лагера, и дрожжи работают в верхней части чана. Эли обычно имеют более насыщенный, "
            "фруктовый вкус и аромат."
        )
    
    elif "стаут" in text:
        await update.message.reply_text(
            "Стаут - это тёмное пиво, приготовленное с использованием жареного ячменя. "
            "Имеет богатый, плотный вкус с нотами кофе, шоколада и солода. "
            "Изначально термин 'стаут' означал просто 'крепкий пиво'."
        )
    
    elif "портер" in text:
        await update.message.reply_text(
            "Портер - это тёмное пиво, предшественник стаута. Получил популярность среди "
            "лондонских носильщиков (porter в переводе с английского - носильщик). "
            "Характеризуется сложным вкусом с нотами карамели, шоколада и иногда лёгкой дымностью."
        )
    
    elif "пшеничное" in text:
        await update.message.reply_text(
            "Пшеничное пиво производится с использованием значительной доли пшеничного солода. "
            "Обычно легкое, освежающее, с высокой карбонизацией. Немецкие сорта (Weissbier) часто имеют "
            "ноты банана и гвоздики из-за особых штаммов дрожжей."
        )
    
    elif "алкоголь" in text or "градус" in text:
        await update.message.reply_text(
            "Содержание алкоголя в пиве обычно составляет от 3% до 12%. "
            "Легкое пиво может содержать 3-4%, обычные лагеры - около 5%, "
            "крафтовые сорта часто имеют 6-9%, а некоторые специальные сорта могут "
            "достигать 12% и выше. Помните о ответственном потреблении!"
        )
    
    elif "закуска" in text or "закусывать" in text:
        await update.message.reply_text(
            "Традиционные закуски к пиву зависят от страны и сорта пива. "
            "К лагерам хорошо подходят снеки, орешки, легкие сыры. К элям - более острые "
            "и пикантные закуски. К стаутам - шоколад и десерты. "
            "В Германии популярны колбаски и претцели, в Бельгии - сыры и морепродукты."
        )
    
    # Fallback for unrecognized queries
    else:
        await update.message.reply_text(
            "Извините, я не совсем понял ваш вопрос. Попробуйте сформулировать иначе или "
            "воспользуйтесь командой /menu, чтобы увидеть доступные темы."
        )

def main() -> None:
    """Start the bot."""
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    logger.info("Web server thread started")
    
    # Create the Application with more robust settings
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    
    # Add callback query handler for inline keyboard buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler for regular text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler to log errors
    async def error_handler(update, context):
        logger.error(f"Exception while handling an update: {context.error}")

    application.add_error_handler(error_handler)

    # Start the Bot with more reliable settings
    logger.info("Starting Telegram Beer Bot")
    application.run_polling(allowed_updates=Update.ALL_TYPES, 
                           drop_pending_updates=True,
                           pool_timeout=30,
                           read_timeout=30,
                           write_timeout=30)

if __name__ == "__main__":
    main()