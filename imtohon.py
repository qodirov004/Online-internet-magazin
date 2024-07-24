import asyncio
import logging
import sqlite3
import requests
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from bs4 import BeautifulSoup as bt

TOKEN = "7389139111:AAGtFXwdDHL0eW8gSfM2RGxJl9zbAGcQZHE"

bot = Bot(
    token=TOKEN,
    session=AiohttpSession(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()
router = Router()
dp.include_router(router)

logging.basicConfig(level=logging.DEBUG)

user_carts = {}
user_data = {}



def create_keyboard(buttons):
    keyboard = InlineKeyboardBuilder()
    for button in buttons:
        keyboard.button(**button)
    return keyboard.as_markup()

menyu = create_keyboard(
    [
        {"text": "🛍 Shop", "callback_data": "shop"},
        {"text": "🛒 Savat", "callback_data": "savat"},
        {"text": "Admin", "url" : "t.me/shoh_qodirov"}
    ]
)

main_menu_keyboard = create_keyboard(
    [
        {"text": "🛍 Shop", "callback_data": "shop"},
        {"text": "🛒 Savat", "callback_data": "savat"},
        {"text": "Admin", "url" : "t.me/shoh_qodirov"},
    ]
)

backeee = create_keyboard([{"text": "🔙 Orqaga", "callback_data": "back"}])

def fetch_products():
    try:
        url = requests.get("https://dummyjson.com/products")
        response = url.json()
        products = {}
        maxsulotlar = InlineKeyboardBuilder()
        for i in response["products"]:
            products[i["title"]] = {
                "price": i["price"],
                "description": i["description"],
                "image": i["images"][0],
            }
            maxsulotlar.button(text=i["title"], callback_data=i["title"])
        maxsulotlar.add(InlineKeyboardButton(text="🛒 Savat", callback_data="savat"))
        maxsulotlar.add(InlineKeyboardButton(text="🔙 Orqaga", callback_data="ortga"))
        maxsulotlar.adjust(3)
        return products, maxsulotlar.as_markup()
    except requests.RequestException as e:
        logging.error(f"Error fetching products: {e}")
        return {}, InlineKeyboardMarkup()

products, maxsulotlar = fetch_products()

product_details_builder = create_keyboard(
    [
        {"text": "Savatga qoshish", "callback_data": "add_to_cart"},
        {"text": "🔙 Orqaga", "callback_data": "ortga"},
    ]
)



@router.message(CommandStart())
async def send_welcome(message: Message):
    try:
        user_id = message.from_user.id
        user_data[user_id] = {
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "username": message.from_user.username,
        }
        await message.answer(
            "Assalomu aleykum Online magazin botimizga xush kelibsiz",
            reply_markup=menyu,
        )
    except Exception as e:
        logging.error(f"Error in send_welcome: {e}")

@router.callback_query(lambda c: c.data == "shop")
async def shopping(call: CallbackQuery):
    try:
        await call.message.answer_photo(
            photo="https://uzum.uz/media/wp-content/uploads/2023/12/fishki-uzum-marketa-1-1838x810.png",
            caption="Istalgan birini tanlang",
            reply_markup=maxsulotlar,
        )
    except Exception as e:
        logging.error(f"Error in shopping: {e}")

@router.callback_query(lambda c: c.data.startswith("set:"))
async def handle_set(call: CallbackQuery):
    try:
        await call.answer(f"Set: {call.data.split(':')[1]}")
    except Exception as e:
        logging.error(f"Error in handle_set: {e}")

@router.callback_query(lambda c: c.data in products.keys())
async def handle_product_selection(call: CallbackQuery):
    try:
        product_title = call.data
        product = products.get(product_title)
        if product:
            photo_url = product['image']
            await call.message.answer_photo(
                photo=photo_url,
                caption=f"Mahsulot: {product_title}\n\nNarxi: {product['price']} $\nTavsif: {product['description']}",
                reply_markup=product_details_builder
            )
        else:
            await call.answer("Mahsulot topilmadi.")
    except Exception as e:
        logging.error(f"Error handling product selection: {e}")
        await call.answer("Xato yuz berdi.")

@router.callback_query(lambda c: c.data == "add_to_cart")
async def add_to_cart(call: CallbackQuery):
    try:
        user_id = call.from_user.id
        product_caption = call.message.caption
        if user_id not in user_carts:
            user_carts[user_id] = {}

        if product_caption not in user_carts[user_id]:
            user_carts[user_id][product_caption] = 1
        else:
            user_carts[user_id][product_caption] += 1

        await call.answer("Mahsulot savatga qo'shildi!")
    except Exception as e:
        logging.error(f"Error in add_to_cart: {e}")

@router.callback_query(lambda c: c.data == "savat")
async def view_cart(call: CallbackQuery):
    try:
        user_id = call.from_user.id
        cart_items = user_carts.get(user_id, {})
        if not cart_items:
            await call.message.answer("Sizning savatingiz bo'sh.")
        else:
            total_cost = 0
            for item, quantity in cart_items.items():
                for title, product in products.items():
                    if product["description"] in item:
                        total_price = product["price"] * quantity
                        total_cost += total_price
                        item_message = (
                            f"{item}\n\nMiqdori: {quantity}\nUmumiy narx: {total_price} $"
                        )
                        cart_keyboard = InlineKeyboardBuilder()
                        cart_keyboard.button(text="-", callback_data=f"decrease_{title}")
                        cart_keyboard.button(text="+", callback_data=f"increase_{title}")
                        cart_keyboard.add(
                            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back")
                        )
                        cart_keyboard = cart_keyboard.as_markup()
                        await call.message.answer(item_message, reply_markup=cart_keyboard)
            await call.message.answer(f"Savatdagi jami narx: {total_cost} $")
    except Exception as e:
        logging.error(f"Error in view_cart: {e}")



@router.callback_query(
    lambda c: c.data.startswith("increase_") or c.data.startswith("decrease_")
)
async def change_quantity(call: CallbackQuery):
    try:
        user_id = call.from_user.id
        action, product_title = call.data.split("_", 1)
        for item, quantity in list(user_carts[user_id].items()):
            if products[product_title]["description"] in item:
                if action == "increase":
                    user_carts[user_id][item] += 1
                elif action == "decrease":
                    if quantity > 1:
                        user_carts[user_id][item] -= 1
                    else:
                        del user_carts[user_id][item]
                break
        await view_cart(call)
    except Exception as e:
        logging.error(f"Error in change_quantity: {e}")

@router.callback_query(lambda c: c.data == "ortga")
async def go_back(call: CallbackQuery):
    try:
        await call.message.answer("Bosh menyu", reply_markup=handle_product_selection())
    except Exception as e:
        logging.error(f"Error in go_back: {e}")




if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))  