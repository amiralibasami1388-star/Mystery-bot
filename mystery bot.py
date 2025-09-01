import telebot
from telebot import types
import time

bot = telebot.TeleBot('8481049172:AAEUGSZx-14B7Sx4-8AAl27ILUGTMgD_H0I')

# حافظه موقت برای امتیاز، تایمر، معمای فعال و وضعیت قفل
user_scores = {}
user_timers = {}
user_active_riddle = {}
user_locked_riddles = {}
user_report = {}

riddles = {
    "معمای ۱": {"question": "من هر روز یک بار می‌آیم، اما هیچ‌وقت نمی‌مانم. همیشه در حرکت هستم، ولی پا ندارم.", "answer": "خورشید"},
    "معمای ۲": {"question": "چه چیزی پر است از سوراخ، ولی آب را نگه می‌دارد؟", "answer": "اسفنج"},
    "معمای ۳": {"question": "من را می‌شکنی، اما صدایم را نمی‌شنوی. من کی‌ام؟", "answer": "سکوت"},
    "معمای ۴": {"question": "چه چیزی همیشه جلو می‌ره ولی هیچ‌وقت برنمی‌گرده؟", "answer": "زمان"},
    "معمای ۵": {"question": "چه چیزی هرچه بیشتر برداری، بزرگ‌تر نمی‌شه بلکه کوچک‌تر می‌شه؟", "answer": "چاله"},
    "معمای ۶": {"question": "چه چیزی بدون زبان حرف می‌زنه و بدون گوش می‌شنوه؟", "answer": "پژواک"},
    "معمای ۷": {"question": "چه چیزی هرچه بیشتر ازش برداری، بزرگ‌تر نمی‌شه بلکه کوچک‌تر می‌شه؟", "answer": "چاله"},
    "معمای ۸": {"question": "چه چیزی همیشه در حال حرکت است ولی هیچ‌وقت نمی‌رسد؟", "answer": "فردا"},
    "معمای ۹": {"question": "چه چیزی بدون نفس زنده است و بدون دهان حرف می‌زند؟", "answer": "اکو"},
    "معمای ۱۰": {"question": "چه چیزی وقتی خشک است وزنش بیشتر است؟", "answer": "اسفنج"}
}

def show_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for riddle in riddles.keys():
        markup.add(types.KeyboardButton(riddle))
    markup.add(types.KeyboardButton("📋 کارنامه من"))
    bot.send_message(chat_id, "🎯 یکی از معماهای زیر رو انتخاب کن:", reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(msg):
    chat_id = msg.chat.id
    user_scores[chat_id] = {"correct": 0, "wrong": 0}
    user_locked_riddles[chat_id] = set()
    user_report[chat_id] = {}
    show_main_menu(chat_id)

@bot.message_handler(func=lambda message: message.text in riddles.keys())
def ask_riddle(message):
    chat_id = message.chat.id
    riddle_key = message.text

    if chat_id in user_locked_riddles and riddle_key in user_locked_riddles[chat_id]:
        bot.send_message(chat_id, "🔒 شما قبلاً این معما رو دیدید یا جواب دادید. نمی‌تونید دوباره تلاش کنید.")
        return

    user_timers[chat_id] = time.time()
    user_active_riddle[chat_id] = riddle_key

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("👀 دیدن جواب"))
    bot.send_message(chat_id, f"🧩 {riddle_key}:\n{riddles[riddle_key]['question']}\n\nاگه جواب داری، همینجا بنویس!", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "👀 دیدن جواب")
def show_answer(message):
    chat_id = message.chat.id
    riddle_key = user_active_riddle.get(chat_id)

    if not riddle_key:
        bot.send_message(chat_id, "❌ معمای فعالی پیدا نشد. لطفاً یکی از معماها رو انتخاب کن.")
        show_main_menu(chat_id)
        return

    answer = riddles[riddle_key]["answer"]
    bot.send_message(chat_id, f"✅ جواب {riddle_key}:\n{answer}")

    # ثبت در کارنامه
    user_report[chat_id][riddle_key] = {
        "status": "👀 جواب دیده شد",
        "time": None
    }

    user_locked_riddles.setdefault(chat_id, set()).add(riddle_key)
    user_active_riddle.pop(chat_id, None)
    user_timers.pop(chat_id, None)
    show_main_menu(chat_id)

@bot.message_handler(func=lambda message: message.text == "📋 کارنامه من")
def show_report(message):
    chat_id = message.chat.id
    report = user_report.get(chat_id, {})
    if not report:
        bot.send_message(chat_id, "📭 هنوز هیچ معمایی حل نکردی یا جوابش رو ندیدی.")
        return

    result = "📊 کارنامه شما:\n\n"
    for key in riddles.keys():
        if key in report:
            status = report[key]["status"]
            time_taken = report[key]["time"]
            time_str = f"⏱ زمان: {int(time_taken)} ثانیه" if time_taken else ""
            result += f"🔹 {key}: {status} {time_str}\n"
        else:
            result += f"🔸 {key}:  هنوز پاسخ داده نشده\n"

    correct = user_scores.get(chat_id, {}).get("correct", 0)
    wrong = user_scores.get(chat_id, {}).get("wrong", 0)
    result += f"\n✅ درست‌ها: {correct} | ❌ غلط‌ها: {wrong}"

    bot.send_message(chat_id, result)

@bot.message_handler(func=lambda message: True)
def check_answer(message):
    chat_id = message.chat.id
    riddle_key = user_active_riddle.get(chat_id)
    start_time = user_timers.get(chat_id)

    if not riddle_key or not start_time:
        bot.send_message(chat_id, "❗ لطفاً اول یک معما انتخاب کن.")
        show_main_menu(chat_id)
        return

    elapsed = time.time() - start_time
    if elapsed > 30:
        bot.send_message(chat_id, "⏰ زمان پاسخ‌گویی تموم شد! لطفاً معمای دیگه‌ای رو امتحان کن.")
        user_scores[chat_id]["wrong"] += 1
        user_report[chat_id][riddle_key] = {
            "status": "⏰ دیر پاسخ داد",
            "time": elapsed
        }
        user_locked_riddles.setdefault(chat_id, set()).add(riddle_key)
        user_active_riddle.pop(chat_id, None)
        user_timers.pop(chat_id, None)
        show_main_menu(chat_id)
        return

    correct_answer = riddles[riddle_key]["answer"].strip().lower()
    user_response = message.text.strip().lower()

    if correct_answer == user_response:
        bot.send_message(chat_id, f"🎉 آفرین! جواب درست بود: {correct_answer}")
        user_scores[chat_id]["correct"] += 1
        status = "✅ درست پاسخ داد"
    else:
        bot.send_message(chat_id, f"❌ نه، جواب درست نبود. جواب صحیح بود: {correct_answer}")
        user_scores[chat_id]["wrong"] += 1
        status = "❌ غلط پاسخ داد"

    user_report[chat_id][riddle_key] = {
        "status": status,
        "time": elapsed
    }

    user_locked_riddles.setdefault(chat_id, set()).add(riddle_key)
    user_active_riddle.pop(chat_id, None)
    user_timers.pop(chat_id, None)
    show_main_menu(chat_id)

bot.infinity_polling()
