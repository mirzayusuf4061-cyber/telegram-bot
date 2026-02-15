
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
import os

TOKEN = "8173974361:AAER7WriV47EKKl5JjKaHRBflLdTR18Cv20"

# Qiyinlik darajalari 40 savol uchun
difficulties = [
    -1.5,-1.2,-1,-0.8,-0.5,-0.3,-0.2,0,0.1,0.2,
    0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,
    -1,-0.7,-0.4,-0.1,0.2,0.5,0.8,1.1,1.4,-1.3,
    -0.9,-0.6,-0.2,0.3,0.6,0.9,1.3,-1.4,1.5,0
]

RESULTS_FILE = "results.json"

def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_results(results):
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f)

# Harflarni raqamga aylantirish
def answer_to_number(letter, index):
    letter = str(letter).upper()
    if 0 <= index <= 31:
        mapping = {"A":1, "B":0, "C":0, "D":0}
    elif 32 <= index <= 34:
        mapping = {"A":1, "B":0, "C":0, "D":0, "E":0, "F":0}
    else:
        try:
            return float(letter)
        except:
            return 0
    return mapping.get(letter,0)

def calculate_ability(answers):
    score = 0
    for i in range(len(answers)):
        score += answers[i]-difficulties[i] if answers[i]==1 else -difficulties[i]
    return score/len(answers)

def convert_to_90_scale(theta):
    return round((theta+3)/6*90,2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Rasch Model Bot\n\n"
        "40 ta javob yuboring:\n"
        "1–32: A–D\n33–35: A–F\n36–40: yozma javoblar\n"
        "Format:\n/check exam1 ABCD...ABCDE12345\n\n"
        "Foydalanuvchi ID bilan natijalar saqlanadi."
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        exam_id = context.args[0]
        text = context.args[1]

        if len(text) < 40:
            await update.message.reply_text("❌ 40 ta javob yuboring.")
            return

        # Javoblarni bo‘lish: 1–35 harflar, 36–40 yozma javob
        answers_letters = text[:35]
        answers_written = text[35:]

        answers_all = [answer_to_number(ltr, idx) for idx,ltr in enumerate(answers_letters)]
        # Oxirgi 5 savol yozma javob sifatida float saqlash
        for i, ltr in enumerate(answers_written):
            answers_all.append(answer_to_number(ltr,35+i))

        # Har bir savol feedback
        per_question_feedback = []
        for idx, val in enumerate(answers_all):
            if idx <= 31:
                correct = "A"
                user_val = answers_letters[idx].upper()
                result = "✅" if user_val==correct else "❌"
            elif idx <=34:
                correct = "A"
                user_val = answers_letters[idx].upper()
                result = "✅" if user_val==correct else "❌"
            else:
                correct = "raqam"  # minimal tekshiruv
                user_val = answers_written[idx-35]
                result = "✅"
            per_question_feedback.append(f"{idx+1}:{user_val} {result}")

        feedback_text = "\n".join(per_question_feedback)
        theta = calculate_ability(answers_all)
        final_score = convert_to_90_scale(theta)

        # Natijani saqlash
        user_id = str(update.message.from_user.id)
        user_name = update.message.from_user.full_name
        results = load_results()
        if exam_id not in results:
            results[exam_id] = {}
        results[exam_id][user_id] = {
            "name": user_name,
            "answers": list(text),
            "theta": round(theta,2),
            "score": final_score
        }
        save_results(results)

        await update.message.reply_text(
            f"Har bir savol natijasi:\n{feedback_text}\n\n"
            f"✅ Theta: {round(theta,2)}\n"
            f"90 ballik tizim: {final_score}\n"
            f"Natijangiz saqlandi ({exam_id})."
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Format xato. Misol:\n/check exam1 ABCDE12345\nXato: {str(e)}")

async def results_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        exam_id = context.args[0]
        user_id = str(update.message.from_user.id)
        results = load_results()
        if exam_id in results and user_id in results[exam_id]:
            res = results[exam_id][user_id]
            await update.message.reply_text(
                f"Natijangiz ({exam_id}):\n"
                f"Theta: {res['theta']}\n"
                f"90 ballik tizim: {res['score']}\n"
                f"Javoblar: {''.join(res['answers'])}"
            )
        else:
            await update.message.reply_text("Natija topilmadi.")
    except:
        await update.message.reply_text("❌ Format xato. Misol:\n/results exam1")

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        exam_id = context.args[0]
        results = load_results()
        if exam_id not in results or not results[exam_id]:
            await update.message.reply_text("Natijalar mavjud emas.")
            return
        sorted_results = sorted(results[exam_id].values(), key=lambda x: x['theta'], reverse=True)
        ranking_text = f"🏆 Reyting jadvali ({exam_id}):\n"
        for i,res in enumerate(sorted_results,1):
            ranking_text += f"{i}. {res['name']} - Theta: {res['theta']}, Ball: {res['score']}\n"
        await update.message.reply_text(ranking_text)
    except:
        await update.message.reply_text("❌ Format xato. Misol:\n/ranking exam1")

# Botni ishga tushirish
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("check", check))
app.add_handler(CommandHandler("results", results_user))
app.add_handler(CommandHandler("ranking", ranking))
app.run_polling()
