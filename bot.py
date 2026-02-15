from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = "8173974361:AAER7WriV47EKKl5JjKaHRBflLdTR18Cv20"

async def start(update, context):
    await update.message.reply_text("Bot ishlayapti ✅")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
