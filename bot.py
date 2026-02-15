from telegram.ext import Updater, CommandHandler

TOKEN = "8173974361:AAGEDZRUGhh_wBphS3Nq_F-ushRA7xj8d10"

difficulties = [
    -1.5,-1.2,-1,-0.8,-0.5,-0.3,-0.2,0,0.1,0.2,
    0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,
    -1,-0.7,-0.4,-0.1,0.2,0.5,0.8,1.1,1.4,-1.3,
    -0.9,-0.6,-0.2,0.3,0.6,0.9,1.3,-1.4,1.5,0
]

def calculate_ability(answers):
    score = 0
    for i in range(40):
        if answers[i] == 1:
            score += 1 - difficulties[i]
        else:
            score -= difficulties[i]
    return score / 40

def convert_to_90_scale(theta):
    return round((theta + 3) / 6 * 90, 2)

def start(update, context):
    update.message.reply_text(
        "Rasch Model Bot\n\n"
        "40 ta javob yuboring:\n"
        "/check 1,0,1,1,0,..."
    )

def check(update, context):
    try:
        text = context.args[0]
        answers = list(map(int, text.split(',')))

        if len(answers) != 40:
            update.message.reply_text("40 ta javob bo‘lishi kerak.")
            return

        theta = calculate_ability(answers)
        final_score = convert_to_90_scale(theta)

        update.message.reply_text(
            f"Qobiliyat (theta): {round(theta,2)}\n"
            f"90 ballik tizim: {final_score}"
        )

    except:
        update.message.reply_text("Format xato.")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("check", check))

updater.start_polling()
updater.idle()
