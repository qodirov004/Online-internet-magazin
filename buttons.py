import requests
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder



menyu = InlineKeyboardMarkup(
  inline_keyboard=[
    [InlineKeyboardButton(text="shop 🛍", callback_data="shop"), InlineKeyboardButton(text="Site dokon",web_app=WebAppInfo(url="https://uzum.uz/uz"))],
    [InlineKeyboardButton(text="savat ", callback_data="savat"), InlineKeyboardButton(text="admin", url="t.me/shoh_qodirov")]
  ]
)

url = requests.get("https://dummyjson.com/products")
response = url.json()
# print(len(response["products"]))

maxsulotlar = InlineKeyboardBuilder()
for i in response["products"]:
  maxsulotlar.button(text=i['title'], callback_data=i['title'])
maxsulotlar.add(InlineKeyboardButton(text="ortga", callback_data="ortga"))
maxsulotlar.adjust(3)


builder = InlineKeyboardBuilder()

for index in range(1, 11):
    builder.button(text=f"Set {index}", callback_data=f"set:{index}")
builder.add(InlineKeyboardButton(text="ortga", callback_data="ortga"))
builder.adjust(4, 2)
