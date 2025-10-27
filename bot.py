# import telebot
# import logging
# import google.generativeai as genai
# from dotenv import load_dotenv
# import os
# from pedidos import crear_pedido

# # --- CONFIGURACIONES ---
# load_dotenv()

# TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # --- CLIENTES DE API ---
# bot = telebot.TeleBot(TELEGRAM_TOKEN)

# # Configurar Gemini
# genai.configure(api_key=GEMINI_API_KEY)
# model = genai.GenerativeModel("gemini-2.0-flash-lite")

# # --- HANDLERS ---
# @bot.message_handler(commands=["start"])
# def start(message):
#     bot.send_message(
#         message.chat.id,
#         "🍔 ¡Bienvenido a *Tucson Burgers*! Soy tu asistente virtual. ¿Qué te gustaría pedir hoy?",
#         parse_mode="Markdown"
#     )

# @bot.message_handler(func=lambda message: True)
# def responder_con_ia(message):
#     user_text = message.text

#     try:
#         prompt = f"Sos un asistente virtual de un restaurante llamado Tucson Burgers. Respondé de forma amable y natural al cliente: '{user_text}'"
#         respuesta = model.generate_content(prompt)
#         bot.send_message(message.chat.id, respuesta.text)
#         crear_pedido(nombre_cliente=message.chat.first_name, pedido=user_text, domicilio="calle falsa 123")
#     except Exception as e:
#         print("Error con Gemini:", e)
#         bot.send_message(message.chat.id, "😕 Lo siento, hubo un problema al procesar tu pedido. Intentá de nuevo.")

# # --- INICIO DEL BOT ---
# logging.basicConfig(level=logging.INFO)
# print("🤖 Bot de Tucson Burgers iniciado...")
# bot.polling(non_stop=True, interval=1)

from telebot import TeleBot, types

bot = TeleBot("7431103849:AAHUkhFRY4B5w9yRJ3A6c42H32_1stkdotM")

@bot.message_handler(commands=['menu'])
def menu(message):
    comidas = ["Pizza", "Hamburguesa", "Ensalada"]
    for comida in comidas:
        markup = types.InlineKeyboardMarkup()
        for cantidad in range(1, 6):  # Botones del 1 al 5
            markup.add(types.InlineKeyboardButton(text=str(cantidad), callback_data=f"{comida}_{cantidad}"))
        bot.send_message(message.chat.id, comida, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    comida, cantidad = call.data.split("_")
    bot.answer_callback_query(call.id, f"Elegiste {cantidad} de {comida}")

bot.polling(non_stop=True, interval=1)