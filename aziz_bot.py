from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Состояния для FSM
class Form(StatesGroup):
    waiting_for_ff_id = State()
    choosing_product = State()
    confirming_payment = State()

# Список товаров
PRODUCTS = {
    "310 + 31 алмазов 🔥 Хит": 245,
    "100 + 10 алмазов 💎": 76,
    "520 + 52 алмазов 💎": 397,
    "1060 + 106 алмазов 💎": 799,
    "2180 + 218 алмазов 💎": 1599,
    "5600 + 560 алмазов 💎": 3829
}

# Стартовая команда
@dp.message_handler(commands='start')
async def start(message: types.Message, state: FSMContext):
    await message.answer("👋 Добро пожаловать! Введите ваш Free Fire ID:")
    await Form.waiting_for_ff_id.set()

# Получаем FF ID
@dp.message_handler(state=Form.waiting_for_ff_id)
async def get_ff_id(message: types.Message, state: FSMContext):
    await state.update_data(ff_id=message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in PRODUCTS:
        markup.add(KeyboardButton(name))
    await message.answer("💎 Выберите пакет алмазов:", reply_markup=markup)
    await Form.choosing_product.set()

# Выбор товара
@dp.message_handler(state=Form.choosing_product)
async def choose_product(message: types.Message, state: FSMContext):
    if message.text not in PRODUCTS:
        return await message.answer("❌ Пожалуйста, выберите товар из кнопок.")
    
    product = message.text
    price = PRODUCTS[product]
    await state.update_data(product=product)

    await message.answer(
        f"🧾 Вы выбрали: {product}\n💰 Цена: {price} ₽\n\n"
        "💳 Реквизиты для оплаты:\n8600 1234 5678 9012\n\n"
        "📸 Пожалуйста, пришлите чек и ожидайте подтверждения.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await Form.confirming_payment.set()

# Получение чека
@dp.message_handler(content_types=types.ContentType.PHOTO, state=Form.confirming_payment)
async def receive_payment(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    ff_id = user_data['ff_id']
    product = user_data['product']

    caption = (
        f"📥 Новый заказ:\n"
        f"👤 @{message.from_user.username or message.from_user.id}\n"
        f"🆔 Free Fire ID: {ff_id}\n"
        f"📦 Товар: {product}\n"
        f"✅ Чек:"
    )
    await bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption)
    await message.answer("✅ Спасибо! Ваш чек отправлен. Ожидайте подтверждения.")
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
