import telebot
import logging
import google.generativeai as genai
import re
from datetime import datetime, time
import config
from controllers import getShifts, createShift

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)
genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")
logging.basicConfig(level=logging.INFO)

turnos_reservados = getShifts()

def turno_ocupado(dia, hora):
    """Devuelve True si el turno ya está tomado."""
    return any(t["dia"] == dia and t["hora"] == hora for t in turnos_reservados)

def horario_valido(hora):
    """Devuelve True si está dentro del horario laboral (08:00 a 16:00)."""
    try:
        hora_dt = datetime.strptime(hora, "%H:%M").time()
        return time(8, 0) <= hora_dt <= time(16, 0)
    except:
        return False
historial_chat = {}
hoy = datetime.today().strftime("%Y-%m-%d")
# --- HANDLER GEMINI ---
@bot.message_handler(func=lambda msg: True)
def manejar_mensaje(message):
    cliente = message.from_user.first_name or "Cliente"
    chat_id = message.chat.id
    
    if chat_id not in historial_chat:
        historial_chat[chat_id] = []

    historial_chat[chat_id].append({"rol": "usuario", "mensaje": message.text})

    historial_texto = ""
    for entry in historial_chat[chat_id]:
        rol = entry["rol"]
        msg = entry["mensaje"]
        if rol == "usuario":
            historial_texto += f"Cliente: {msg}\n"
        else:
            historial_texto += f"Asistente: {msg}\n"

    print("💬 Historial de chat:\n", historial_texto)
    prompt = f"""
    Sos el asistente virtual de la barbería *Tucson* 💈.
    Gestionás turnos para cortes de pelo masculinos.
    📅 Turnos ya reservados: {turnos_reservados}.
    🕗 Horario laboral: de 08:00 a 16:00 (cada 30 minutos).
    📆 Fecha actual: {hoy}
    Cliente: {cliente}
    Historial de chat:
    {historial_texto}

    Tu tarea:
    - Responde de manera coherente y continua la conversación con el cliente.
    - Si el cliente pide un turno (día y hora), verificá que:
    1. El horario esté dentro del rango laboral.
    2. No esté ocupado para ese día.
    - Si todo está correcto, devolvé una respuesta amable confirmando el turno
    y al final incluí este bloque de texto, en formato claro:
        ACCION: reservar
        NOMBRE: nombre_cliente
        DIA: YYYY-MM-DD
        HORA: HH:MM
    - Si el horario pedido está fuera del rango laboral, sugerí uno dentro del rango.
    - Si el horario está ocupado, ofrecé el más cercano libre.
    - Si el mensaje no tiene que ver con reservar turnos, respondé normalmente.
    """


    respuesta = model.generate_content(prompt)
    texto = respuesta.text or "No entendí bien, ¿podés repetirlo?"
    logging.info(f"Gemini respondió: {texto}")

    historial_chat[chat_id].append({"rol": "asistente", "mensaje": texto})

    match = re.search(
    r"ACCION:\s*(.+)\nNOMBRE:\s*(.+)\nDIA:\s*(\d{4}-\d{2}-\d{2})\nHORA:\s*(\d{2}:\d{2})",
    texto,
    re.IGNORECASE
)

    if match:
        accion, nombre, dia, hora = [x.strip() for x in match.groups()]
        if accion.lower() == "reservar":
            nombre = nombre or cliente

            # Validaciones
            if not dia or not hora:
                bot.send_message(message.chat.id, "⚠️ Falta la fecha o la hora del turno.")
                return

            if not horario_valido(hora):
                bot.send_message(message.chat.id, f"🕗 El horario {hora} está fuera del horario laboral (08:00–16:00).")
                return

            if turno_ocupado(dia, hora):
                bot.send_message(message.chat.id, f"😕 El turno {hora} del {dia} ya está ocupado.")
                return

            # Guardar y confirmar
            createShift(nombre,chat_id, dia, hora)
            bot.send_message(
                message.chat.id,
                f"💈 Turno reservado para *{nombre}* el *{dia}* a las *{hora}* ✅",
                parse_mode="Markdown"
            )
            return

    bot.send_message(message.chat.id, texto)

print("💈 Bot Don Facu listo (modo multi-día, validación de horarios y Gemini)...")
bot.infinity_polling()
