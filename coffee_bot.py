import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)

# === Ýòàïû äèàëîãà ===
AMERICANO, CAPPUCCINO, FLATWHITE, TO_KITCHEN, FROM_KITCHEN = range(5)

# === Ñòàðò ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ïðèâåò! Äàâàé ïîñ÷èòàåì êîôå ?\nÑêîëüêî àìåðèêàíî?"
    )
    return AMERICANO

# === Âîïðîñ 1 ===
async def americano(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["americano"] = update.message.text
    await update.message.reply_text("Ñêîëüêî êàïó÷èíî?")
    return CAPPUCCINO

# === Âîïðîñ 2 ===
async def cappuccino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cappuccino"] = update.message.text
    await update.message.reply_text("Ñêîëüêî ôëåòâàéò?")
    return FLATWHITE

# === Âîïðîñ 3 ===
async def flatwhite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["flatwhite"] = update.message.text
    skip_button = [[KeyboardButton("Ïðîïóñòèòü ??")]]
    await update.message.reply_text(
        "×òî ïåðåäàâàëîñü íà êóõíþ?",
        reply_markup=ReplyKeyboardMarkup(skip_button, one_time_keyboard=True, resize_keyboard=True)
    )
    return TO_KITCHEN

# === Âîïðîñ 4 ===
async def to_kitchen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["to_kitchen"] = None if text == "Ïðîïóñòèòü ??" else text

    skip_button = [[KeyboardButton("Ïðîïóñòèòü ??")]]
    await update.message.reply_text(
        "×òî áðàëè ñ êóõíè?",
        reply_markup=ReplyKeyboardMarkup(skip_button, one_time_keyboard=True, resize_keyboard=True)
    )
    return FROM_KITCHEN

# === Âîïðîñ 5 è Èòîãè ===
async def from_kitchen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["from_kitchen"] = None if text == "Ïðîïóñòèòü ??" else text

    # === Ïîäñ÷¸ò ===
    try:
        americano = int(context.user_data.get("americano", 0))
        cappuccino = int(context.user_data.get("cappuccino", 0))
        flatwhite = int(context.user_data.get("flatwhite", 0))
    except ValueError:
        await update.message.reply_text("Îøèáêà: íóæíî ââîäèòü òîëüêî öèôðû ?")
        return ConversationHandler.END

    total_coffee = americano + cappuccino + flatwhite

    # === Ðàñ÷¸ò ìîëîêà ===
    milk_total = cappuccino * 150 + flatwhite * 120

    # === Ôîðìèðîâàíèå ðåçóëüòàòà ===
    result = f"? Êîôå øòàò: {total_coffee} øò.\n"
    result += f"?? Ìîëîêî: {milk_total} ìë\n"

    if context.user_data.get("to_kitchen"):
        result += f"?? Ïåðåìåùåíèå íà êóõíþ: {context.user_data['to_kitchen']}\n"
        if context.user_data.get("from_kitchen"):
            result += f"?? Ïåðåìåùåíèå íà áàð: {context.user_data['from_kitchen']}"
    else:
        result += f"?? Ïåðåìåùåíèå íà áàð: {context.user_data.get('from_kitchen', '-')}"

    # === Êíîïêà "Íà÷àòü çàíîâî" ===
    restart_button = [[KeyboardButton("Íà÷àòü çàíîâî ??")]]
    await update.message.reply_text(
        result,
        reply_markup=ReplyKeyboardMarkup(restart_button, one_time_keyboard=True, resize_keyboard=True)
    )
    return ConversationHandler.END

# === Ïåðåçàïóñê ===
async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ïðîñòî çàïóñêàåì ñöåíàðèé ñ íà÷àëà
    return await start(update, context)

# === Îòìåíà ===
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Îïðîñ îòìåí¸í.")
    return ConversationHandler.END

# === Îñíîâíîé çàïóñê ===
def main():
app = ApplicationBuilder().token(os.getenv("TOKEN")).build()

conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^Íà÷àòü çàíîâî ??$"), restart)
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



