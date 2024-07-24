import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import Command
from config import BOT_TOKEN as token
from buttons import menyu, maxsulotlar, builder
import requests
from googletrans import Translator



logging.basicConfig(level=logging.INFO)

bot = Bot(token=token)

dp = Dispatcher()

# translate = Translator()

# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer_photo(photo="https://www.spot.uz/media/img/2022/08/85brvW16603795118030_b.jpg", caption="Dokonimizga Xush kelibsiz", reply_markup=menyu)



# @dp.callback_query(F.data == 'shop')
# async def Shopping(call: types.CallbackQuery):
#     await call.message.answer_photo(photo="https://uzum.uz/media/wp-content/uploads/2023/12/fishki-uzum-marketa-1-1838x810.png", caption="Istalgan birini tanlang", reply_markup=maxsulotlar.as_markup())
#     await call.message.delete()



# @dp.callback_query(F.data)
# async def Xarid(call: types.CallbackQuery):
#   maxx = call.data
#   url = requests.get("https://dummyjson.com/products")
#   response = url.json()
#   for i in response['products']:
#      if maxx == i["title"]:
#         translate = Translator.translate(maxx[0]["description"], dest = "uz")
#         await call.message.answer_photo(photo=i['images'][0], caption=f"haqida: {translate}\nNarxi: {i['price']} $", reply_markup=builder.as_markup())

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime


TOKEN = '7356572627:AAEVtmuzENQrRpbAGFInBegS0YINfK2RFVs'


bus_schedule = {
    'qoshkopir': ['08:00', '08:25', '08:50', '09:15', '09:40', '10:05', '10:30', '10:55', '11:20', '11:45', '12:10', '12:35', '13:00', '13:25', '13:50', '14:15', '14:40', '15:05', '15:30', '15:55', '16:20', '16:45', '17:10', '17:35', '18:00', '18:25', '18:50'
],
    'urganch': ['08:10', '08:35', '09:00', '09:25', '09:50', '10:15', '10:40', '11:05', '11:30', '11:55', '12:20', '12:45', '13:10', '13:35', '14:00', '14:25', '14:50', '15:15', '15:40', '16:05', '16:30', '16:55', '17:20', '17:45', '18:10', '18:35'
]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Qoshkopir", callback_data='qoshkopir')],
        [InlineKeyboardButton("Urganch", callback_data='urganch')],
        [InlineKeyboardButton("Ikki shahar jadvali", callback_data='both')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Qaysi manzilni tanlaysiz?', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    destination = query.data
    
    if destination == 'both':
        qoshkopir_schedule = format_schedule('Qoshkopir', bus_schedule['qoshkopir'])
        urganch_schedule = format_schedule('Urganch', bus_schedule['urganch'])
        await query.edit_message_text(text=f"{qoshkopir_schedule}\n\n{urganch_schedule}")
    else:
        now = datetime.now().strftime('%H:%M')
        next_bus = get_next_bus(bus_schedule[destination], now)
        if next_bus:
            await query.edit_message_text(text=f"Eng yaqin avtobus {destination.capitalize()} uchun {next_bus} da keladi.")
        else:
            await query.edit_message_text(text=f"Bugungi kun uchun boshqa avtobus yo'q {destination.capitalize()} uchun.")

def get_next_bus(schedule, current_time):
    for bus_time in schedule:
        if bus_time > current_time:
            return bus_time
    return schedule[0] 

def format_schedule(location, schedule):
    return f"{location} jadvali:\n" + "\n".join(schedule)

def main() -> None:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == '__main__':
    main()


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
      asyncio.run(main())
    except:
        print("tugadi")
