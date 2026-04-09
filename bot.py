import telebot
import re

TOKEN = "8507781006:AAHxkzIKemjWbNbonFkBSrAPvmEO9tjTYF4"
ASSEMBLY_API = "675c28ccc7e0456bb99e83fbf0c79324"

bot = telebot.TeleBot(TOKEN)

def extrair_gasto(texto):
    texto = texto.lower()

    # pegar valor
    valor = re.findall(r'\d+', texto)
    valor = valor[0] if valor else None

    # categorias simples
    if "almoço" in texto or "comida" in texto or "lanche" in texto:
        categoria = "Alimentação"
    elif "uber" in texto or "gasolina" in texto:
        categoria = "Transporte"
    elif "mercado" in texto:
        categoria = "Mercado"
    else:
        categoria = "Outros"

    return valor, categoria

@bot.message_handler(func=lambda m: True)
def responder(mensagem):
    texto = mensagem.text

    valor, categoria = extrair_gasto(texto)

    if valor:
        resposta = f"💰 Anotado: R${valor} - {categoria}"
    else:
        resposta = "Não entendi. Tente algo como: 'gastei 50 no almoço'"

    bot.reply_to(mensagem, resposta)

bot.infinity_polling()
