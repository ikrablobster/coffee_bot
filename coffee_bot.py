import threading
import os
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

def run_web():
    app = Flask("keepalive")
    @app.route("/")
    def index():
        return "ok"
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

# === Этапы диалога ===
AMERICANO, CAPPUCCINO, FLATWHITE, TO_KITCHEN, FROM_KITCHEN = range(5)

# Кнопки
def base_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Пропустить ⏭"), KeyboardButton("Перезапустить бота 🔁")]],
        resize_keyboard=True
    )

# --- Старт ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "☕️ Давай просчитаем расход кофе и молока!\n\n"
        "Сколько американо?",
        reply_markup=base_keyboard()
    )
    return AMERICANO

# --- 1. Американо ---
async def americano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Пропустить ⏭":
        context.user_data["americano"] = 0
    elif text == "Перезапустить бота 🔁":
        return await restart(update, context)
    else:
        context.user_data["americano"] = int(text)

    await update.message.reply_text(
        "Сколько капучино?",
        reply_markup=base_keyboard()
    )
    return CAPPUCCINO

# --- 2. Капучино ---
async def cappuccino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Пропустить ⏭":
        context.user_data["cappuccino"] = 0
    elif text == "Перезапустить бота 🔁":
        return await restart(update, context)
    else:
        context.user_data["cappuccino"] = int(text)

    await update.message.reply_text(
        "Сколько флетвайт?",
        reply_markup=base_keyboard()
    )
    return FLATWHITE

# --- 3. Флетвайт ---
async def flatwhite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Пропустить ⏭":
        context.user_data["flatwhite"] = 0
    elif text == "Перезапустить бота 🔁":
        return await restart(update, context)
    else:
        context.user_data["flatwhite"] = int(text)

    await update.message.reply_text(
        "Что передавалось на кухню?",
        reply_markup=base_keyboard()
    )
    return TO_KITCHEN

# --- 4. На кухню ---
async def to_kitchen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Пропустить ⏭":
        context.user_data["to_kitchen"] = None
    elif text == "Перезапустить бота 🔁":
        return await restart(update, context)
    else:
        context.user_data["to_kitchen"] = text

    await update.message.reply_text(
        "Что бралось с кухни?",
        reply_markup=base_keyboard()
    )
    return FROM_KITCHEN

# --- 5. С кухни ---
async def from_kitchen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Пропустить ⏭":
        context.user_data["from_kitchen"] = None
    elif text == "Перезапустить бота 🔁":
        return await restart(update, context)
    else:
        context.user_data["from_kitchen"] = text

    # --- Подсчёт ---
    americano = context.user_data.get("americano", 0)
    cappuccino = context.user_data.get("cappuccino", 0)
    flatwhite = context.user_data.get("flatwhite", 0)

    total_coffee = americano + cappuccino + flatwhite
    total_milk = cappuccino * 150 + flatwhite * 120

    result = f"☕️ Кофе: {total_coffee} шт.\n🥛 Молоко: {total_milk} мл\n"

    if context.user_data.get("to_kitchen"):
        result += f"📦 Перемещение на кухню: {context.user_data['to_kitchen']}\n"
    if context.user_data.get("from_kitchen"):
        result += f"🍽 Перемещение на бар: {context.user_data['from_kitchen']}\n"

    await update.message.reply_text(result, reply_markup=base_keyboard())
    return ConversationHandler.END

# --- Перезапуск ---
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🔁 Начнём заново!\n\nСколько американо?",
        reply_markup=base_keyboard()
    )
    return AMERICANO

# === Основной запуск ===
def main():
    app = ApplicationBuilder().token(os.getenv("TOKEN")).build()

    conv = ConversationHandler(
    entry_points=[
        CommandHandler("start", start),
        MessageHandler(filters.Regex("^Начать заново 🔁$"), restart)
    ],
    states={
        AMERICANO: [MessageHandler(filters.TEXT & ~filters.COMMAND, americano)],
        CAPPUCCINO: [MessageHandler(filters.TEXT & ~filters.COMMAND, cappuccino)],
        FLATWHITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, flatwhite)],
        TO_KITCHEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, to_kitchen)],
        FROM_KITCHEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, from_kitchen)],
    },
    fallbacks=[CommandHandler("start", start)],
    )
    
    # Запустить веб-сервер в отдельном потоке, чтобы Render увидел открытый порт
    t = threading.Thread(target=run_web, daemon=True)
    t.start()
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()






