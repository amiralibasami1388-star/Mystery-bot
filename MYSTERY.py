import telebot
from telebot import types
 
bot = telebot.TeleBot('8481049172:AAH0jNFD665Xx1QToMkoAEjmrE2_HLcBJd0')


@bot.message_handler(commands=['start'])
def send_wellcome(message):
    bot.reply_to(message, "به این بات خوش اومدی برای شروع بازی از دکمه های زیر استفاده کن")



if __name__ == '__main__':
    bot.polling()