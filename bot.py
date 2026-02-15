from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = "8173974361:AAGEDZRUGhh_wBphS3Nq_F-ushRA7xj8d10"

async def start(update, context):
    await update.message.reply_text("Bot ishlayapti ✅")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
