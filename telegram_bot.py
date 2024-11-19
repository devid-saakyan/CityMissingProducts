import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

# Укажите токен
BOT_TOKEN = "6064450479:AAFS9B4HGD7d1BEoVYL5qyUPG88otYlJzfU"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Пример списка отзывов
CLIENT_REVIEWS = [
    "Курьер опоздал на 2 часа.",
    "Посылка была повреждена при доставке.",
    "Служба поддержки отказалась помочь с возвратом.",
    "Доставка заняла больше недели.",
    "Очень доволен качеством товара!"
]

# Основные категории и подкатегории
CATEGORIES = {
    "Доставка": ["Задержка доставки", "Проблемы с курьером", "Повреждение посылки"],
    "Качество товара": ["Дефект товара", "Не соответствует описанию", "Проблемы с возвратом"],
    "Обслуживание": ["Грубость сотрудников", "Долгое ожидание", "Проблемы с поддержкой"],
    "Другое": []
}

# Хранилище текущего состояния пользователя
user_state = {}

# Создание клавиатуры для категорий
def create_category_buttons():
    keyboard = InlineKeyboardBuilder()
    for category in CATEGORIES.keys():
        keyboard.button(text=category, callback_data=f"category_{category}")
    keyboard.adjust(1)
    return keyboard.as_markup()

# Создание клавиатуры для подкатегорий
def create_subcategory_buttons(category):
    keyboard = InlineKeyboardBuilder()
    subcategories = CATEGORIES.get(category, [])
    for subcategory in subcategories:
        keyboard.button(text=subcategory, callback_data=f"subcategory_{subcategory}")
    keyboard.button(text="Вернуться назад", callback_data="back_to_main")
    keyboard.adjust(1)
    return keyboard.as_markup()

@router.message(Command("start"))
async def start_command(message: types.Message):
    user_state[message.from_user.id] = {"current_index": 0}
    await send_next_review(message.from_user.id)

async def send_next_review(user_id: int):
    current_index = user_state[user_id]["current_index"]

    if current_index < len(CLIENT_REVIEWS):
        review = CLIENT_REVIEWS[current_index]
        user_state[user_id]["current_index"] += 1
        # Сначала отправляем текст жалобы
        await bot.send_message(user_id, f"Отзыв: {review}")
        # Затем предлагаем выбрать категорию
        await bot.send_message(user_id, "Выберите основную категорию для жалобы:", reply_markup=create_category_buttons())
    else:
        await bot.send_message(user_id, "Все отзывы обработаны. Спасибо!")
        user_state.pop(user_id, None)

@router.callback_query(lambda c: c.data.startswith("category_"))
async def handle_category_selection(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    category = callback_query.data.replace("category_", "")
    user_state[user_id]["selected_category"] = category

    # Отправляем подкатегории для выбранной категории
    await callback_query.message.edit_text(
        f"Вы выбрали категорию: {category}. Теперь выберите подкатегорию:",
        reply_markup=create_subcategory_buttons(category)
    )

@router.callback_query(lambda c: c.data.startswith("subcategory_"))
async def handle_subcategory_selection(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    subcategory = callback_query.data.replace("subcategory_", "")
    selected_category = user_state[user_id]["selected_category"]

    # Сохранение выбора
    print(f"Пользователь {user_id} выбрал: Категория - {selected_category}, Подкатегория - {subcategory}")

    # Переход к следующему отзыву
    await callback_query.answer(f"Вы выбрали подкатегорию: {subcategory}")
    await send_next_review(user_id)

@router.callback_query(lambda c: c.data == "back_to_main")
async def handle_back_to_main(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text(
        "Выберите основную категорию для жалобы:",
        reply_markup=create_category_buttons()
    )

# Обработчик запуска
async def on_startup():
    print("Бот запущен!")

# Запуск бота
async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
