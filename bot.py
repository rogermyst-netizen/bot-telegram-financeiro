import telebot

TOKEN = "8507781006:AAFP4pEb1w_HBAViUKOjZuzuMDJ1arxkYqo"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda m: True)
def responder(mensagem):
    bot.reply_to(mensagem, "🤖 Bot funcionando! Recebi sua mensagem.")

bot.infinity_polling()
