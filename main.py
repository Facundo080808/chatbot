import telebot
import logging
import google.generativeai as genai
import re, json
from datetime import datetime, time
import config


bot = telebot.TeleBot(config.TELEGRAM_TOKEN)
genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-lite")
logging.basicConfig(level=logging.INFO)

# --- FUNCIÓN AUXILIAR ---
def guardar_turno_bd(nombre, dia, hora):
    print(f"💾 Guardando en BD -> Cliente: {nombre}, Día: {dia}, Hora: {hora}")

# --- DATOS SIMULADOS ---
turnos_reservados = [
    {"dia": "2025-10-28", "hora": "10:00", "cliente": "Juan"},
    {"dia": "2025-10-29", "hora": "09:30", "cliente": "Pedro"},
]

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

# --- HANDLER GEMINI ---
@bot.message_handler(func=lambda msg: True)
def manejar_mensaje(message):
    cliente = message.from_user.first_name or "Cliente"

    prompt = f"""
    Sos el asistente virtual de la barbería *Don Facu* 💈.
    Gestionás turnos para cortes de pelo masculinos.

    📅 Turnos ya reservados: {turnos_reservados}.
    🕗 Horario laboral: de 08:00 a 16:00 (cada 30 minutos).
    El cliente se llama {cliente} y escribió: "{message.text}".

    Tu tarea:
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
            guardar_turno_bd(nombre, dia, hora)
            bot.send_message(
                message.chat.id,
                f"💈 Turno reservado para *{nombre}* el *{dia}* a las *{hora}* ✅",
                parse_mode="Markdown"
            )
            return

    bot.send_message(message.chat.id, texto)

print("💈 Bot Don Facu listo (modo multi-día, validación de horarios y Gemini)...")
bot.infinity_polling()
