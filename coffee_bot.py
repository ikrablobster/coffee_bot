from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

# === Этапы диалога ===
AMERICANO, CAPPUCCINO, FLATWHITE, TO_KITCHEN, FROM_KITCHEN = range(5)

# === Старт ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Давай посчитаем кофе ?\nСколько американо?"
    )
    return AMERICANO

# === Вопрос 1 ===
async def americano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["americano"] = update.message.text
    await update.message.reply_text("Сколько капучино?")
    return CAPPUCCINO

# === Вопрос 2 ===
async def cappuccino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cappuccino"] = update.message.text
    await update.message.reply_text("Сколько флетвайт?")
    return FLATWHITE

# === Вопрос 3 ===
async def flatwhite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["flatwhite"] = update.message.text
    skip_button = [[KeyboardButton("Пропустить ??")]]
    await update.message.reply_text(
        "Что передавалось на кухню?",
        reply_markup=ReplyKeyboardMarkup(skip_button, one_time_keyboard=True, resize_keyboard=True)
    )
    return TO_KITCHEN

# === Вопрос 4 ===
async def to_kitchen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["to_kitchen"] = None if text == "Пропустить ??" else text

    skip_button = [[KeyboardButton("Пропустить ??")]]
    await update.message.reply_text(
        "Что брали с кухни?",
        reply_markup=ReplyKeyboardMarkup(skip_button, one_time_keyboard=True, resize_keyboard=True)
    )
    return FROM_KITCHEN

# === Вопрос 5 и Итоги ===
async def from_kitchen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["from_kitchen"] = None if text == "Пропустить ??" else text

    # === Подсчёт ===
    try:
        americano = int(context.user_data.get("americano", 0))
        cappuccino = int(context.user_data.get("cappuccino", 0))
        flatwhite = int(context.user_data.get("flatwhite", 0))
    except ValueError:
        await update.message.reply_text("Ошибка: нужно вводить только цифры ?")
        return ConversationHandler.END

    total_coffee = americano + cappuccino + flatwhite

    # === Расчёт молока ===
    milk_total = cappuccino * 150 + flatwhite * 120

    # === Формирование результата ===
    result = f"? Кофе штат: {total_coffee} шт.\n"
    result += f"?? Молоко: {milk_total} мл\n"

    if context.user_data.get("to_kitchen"):
        result += f"?? Перемещение на кухню: {context.user_data['to_kitchen']}\n"
        if context.user_data.get("from_kitchen"):
            result += f"?? Перемещение на бар: {context.user_data['from_kitchen']}"
    else:
        result += f"?? Перемещение на бар: {context.user_data.get('from_kitchen', '-')}"

    # === Кнопка "Начать заново" ===
    restart_button = [[KeyboardButton("Начать заново ??")]]
    await update.message.reply_text(
        result,
        reply_markup=ReplyKeyboardMarkup(restart_button, one_time_keyboard=True, resize_keyboard=True)
    )
    return ConversationHandler.END

# === Перезапуск ===
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Просто запускаем сценарий с начала
    return await start(update, context)

# === Отмена ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос отменён.")
    return ConversationHandler.END

# === Основной запуск ===
def main():
    app = ApplicationBuilder().token("8170742318:AAGVoMuF4i6PLiLAYr0tErWag20fYAFyJqE").build()

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^Начать заново ??$"), restart)
        ],
        states={
            AMERICANO: [MessageHandler(filters.TEXT & ~filters.COMMAND, americano)],
            CAPPUCCINO: [MessageHandler(filters.TEXT & ~filters.COMMAND, cappuccino)],
            FLATWHITE: [MessageHandler(filters.TEXT & ~filters.COMMAND, flatwhite)],
            TO_KITCHEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, to_kitchen)],
            FROM_KITCHEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, from_kitchen)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()