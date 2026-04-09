import telebot
import re
import requests
import subprocess
import time

TOKEN = "8507781006:AAGGRFC8sr601ICj-jUNP-UHCWsc9ZLdztk"
ASSEMBLY_API = "675c28ccc7e0456bb99e83fbf0c79324"

bot = telebot.TeleBot(TOKEN)

# ---------------------------
# Função de texto
# ---------------------------
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

# ---------------------------
# TEXTO
# ---------------------------
@bot.message_handler(content_types=['text'])
def responder(mensagem):
    texto = mensagem.text

    valor, categoria = extrair_gasto(texto)

    if valor:
        resposta = f"💰 Anotado: R${valor} - {categoria}"
    else:
        resposta = "Não entendi. Ex: 'gastei 50 no almoço'"

    bot.reply_to(mensagem, resposta)

# ---------------------------
# ÁUDIO
# ---------------------------
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        bot.send_message(message.chat.id, "🎧 Processando áudio...")

        file_info = bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        audio_file = requests.get(file_url)

        with open("audio.ogg", "wb") as f:
            f.write(audio_file.content)

        # converter para wav
        subprocess.run(["ffmpeg", "-i", "audio.ogg", "audio.wav"], check=True)

        # upload para AssemblyAI
        headers = {"authorization": ASSEMBLY_API}

        upload = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            data=open("audio.wav", "rb")
        )

        audio_url = upload.json()["upload_url"]

        transcricao = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            json={"audio_url": audio_url, "language_code": "pt"},
            headers=headers
        )

        transcript_id = transcricao.json()["id"]

        # esperar transcrição
        while True:
            resultado = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers=headers
            ).json()

            if resultado["status"] == "completed":
                texto = resultado["text"]
                break
            elif resultado["status"] == "error":
                bot.send_message(message.chat.id, "Erro ao transcrever áudio")
                return

            time.sleep(2)

        # processar gasto
        valor, categoria = extrair_gasto(texto)

        if valor:
            resposta = f"🎤 {texto}\n💰 R${valor} - {categoria}"
        else:
            resposta = f"🎤 {texto}\nNão entendi o gasto"

        bot.send_message(message.chat.id, resposta)

    except Exception as e:
        print("Erro áudio:", e)
        bot.send_message(message.chat.id, "Erro ao processar áudio")

# ---------------------------
# START
# ---------------------------
print("Bot rodando...")
bot.infinity_polling()
