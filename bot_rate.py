import telebot
import requests
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


BOT_TOKEN = "6064450479:AAFS9B4HGD7d1BEoVYL5qyUPG88otYlJzfU"
DJANGO_API_URL = "http://127.0.0.1:8000/api/UpdateReviewCategory"
CHAT_ID = "719274325"

bot = telebot.TeleBot(BOT_TOKEN)


def send_review_to_telegram(order_id, rate, comment, review_id, categories):
    keyboard = InlineKeyboardMarkup()

    # Генерация кнопок категорий
    for category in categories:
        callback_data = f"{review_id}:{category['id']}"
        keyboard.add(InlineKeyboardButton(text=category['name'], callback_data=callback_data))

    text = (
        f"📢 <b>Новый отзыв</b>\n"
        f"📦 <b>Order ID:</b> {order_id}\n"
        f"⭐ <b>Оценка:</b> {rate}\n"
        f"💬 <b>Комментарий:</b> {comment}"
    )

    # Отправка сообщения
    bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=keyboard, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: True)
def handle_review_category(call):
    try:
        review_id, category_id = call.data.split(":")  # Извлечение ID из callback_data
        response = requests.post(
            DJANGO_API_URL,
            json={"review_id": int(review_id), "category_id": int(category_id)}
        )

        if response.status_code == 200:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Категория обновлена для отзыва {review_id}.\nВыбранная категория: {category_id}"
            )
            bot.answer_callback_query(call.id, "Категория успешно обновлена!")
        else:
            bot.answer_callback_query(call.id, "Ошибка обновления категории.", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Произошла ошибка: {e}", show_alert=True)


# if __name__ == "__main__":
#     bot.polling(none_stop=True)
