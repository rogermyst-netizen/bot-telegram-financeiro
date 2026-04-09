import telebot
import re
import requests

TOKEN = "SEU_TOKEN_AQUI"

bot = telebot.TeleBot(TOKEN)

def extrair_gasto(texto):
    texto = texto.lower()

    valor = re.findall(r'\d+', texto)
    valor = valor[0] if valor else None

    if "almoço" in texto or "comida" in texto or "lanche" in texto:
        categoria = "Alimentação"
    elif "uber" in texto or "gasolina" in texto:
        categoria = "Transporte"
    elif "mercado" in texto:
        categoria = "Mercado"
    else:
        categoria = "Outros"

    return valor, categoria


# ✅ TEXTO
@bot.message_handler(content_types=['text'])
def responder(mensagem):
    texto = mensagem.text

    valor, categoria = extrair_gasto(texto)

    if valor:
        resposta = f"💰 Anotado: R${valor} - {categoria}"
    else:
        resposta = "Não entendi. Tente: gastei 50 no almoço"

    bot.reply_to(mensagem, resposta)


# ✅ ÁUDIO
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        bot.send_message(message.chat.id, "🎧 Recebi seu áudio, processando...")

        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        audio_file = requests.get(file_url)

        with open("audio.ogg", "wb") as f:
            f.write(audio_file.content)

        bot.send_message(message.chat.id, "✅ Áudio recebido com sucesso!")

    except Exception as e:
        bot.send_message(message.chat.id, f"Erro no áudio: {e}")


# 🚀 START (SEM WHILE, SEM TRY)
bot.infinity_polling()
