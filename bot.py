import telebot
import re
import requests
import time

# 🔑 TOKENS
TOKEN = "8507781006:AAGGRFC8sr601ICj-jUNP-UHCWsc9ZLdztk"
ASSEMBLY_API = "675c28ccc7e0456bb99e83fbf0c79324"

bot = telebot.TeleBot(TOKEN)


# 🧠 Função para extrair gasto
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


# 💬 TEXTO
@bot.message_handler(content_types=['text'])
def responder(mensagem):
    try:
        texto = mensagem.text

        valor, categoria = extrair_gasto(texto)

        if valor:
            resposta = f"💰 Anotado: R${valor} - {categoria}"
        else:
            resposta = "Não entendi. Tente: 'gastei 50 no almoço'"

        bot.reply_to(mensagem, resposta)

    except Exception as e:
        print(f"Erro texto: {e}")


# 🎧 ÁUDIO (COM TRANSCRIÇÃO REAL)
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        bot.send_message(message.chat.id, "🎧 Processando áudio...")

        # baixar áudio do Telegram
        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        audio_file = requests.get(file_url)

        with open("audio.ogg", "wb") as f:
            f.write(audio_file.content)

        # 🔥 IMPORTANTE: converter para .wav (AssemblyAI funciona melhor)
        import subprocess
        subprocess.run(["ffmpeg", "-i", "audio.ogg", "audio.wav", "-y"])

        # upload para AssemblyAI
        headers = {"authorization": ASSEMBLY_API}

        upload_response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            data=open("audio.wav", "rb")
        )

        audio_url = upload_response.json()['upload_url']

        # iniciar transcrição
        transcript_response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            json={"audio_url": audio_url, "language_code": "pt"},
            headers=headers
        )

        transcript_id = transcript_response.json()['id']

        # aguardar resultado
        while True:
            polling = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers=headers
            ).json()

            if polling['status'] == 'completed':
                texto = polling['text']
                break
            elif polling['status'] == 'error':
                bot.send_message(message.chat.id, "❌ Erro na transcrição")
                return

            time.sleep(2)

        # processar gasto
        valor, categoria = extrair_gasto(texto)

        if valor:
            resposta = f"🎧 Você disse: {texto}\n💰 R${valor} - {categoria}"
        else:
            resposta = f"🎧 Você disse: {texto}\nNão entendi o gasto"

        bot.send_message(message.chat.id, resposta)

    except Exception as e:
        print(f"Erro áudio: {e}")
        bot.send_message(message.chat.id, "❌ Erro ao processar áudio")


# 🚀 START
print("Bot rodando...")
bot.infinity_polling(timeout=30, long_polling_timeout=30)
