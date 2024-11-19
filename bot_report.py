import telebot
import requests
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


BOT_TOKEN = "6064450479:AAFS9B4HGD7d1BEoVYL5qyUPG88otYlJzfU"
DJANGO_API_URL = "http://127.0.0.1:8000/api/UpdateProductReport"
CHAT_ID = "719274325"

bot = telebot.TeleBot(BOT_TOKEN)


def send_report_to_telegram(sap_code_name, category_sap_code_name, price, report_id, image_url, reasons, branch):
    keyboard = InlineKeyboardMarkup()
    print(reasons)
    for reason in reasons:
        print(1)
        print(reason)
        callback_data = f"{report_id}:{reason['id']}"
        keyboard.add(InlineKeyboardButton(text=reason['name'], callback_data=callback_data))

    text = (
        f"📢 <b>Новый возврат</b>\n"
        f"🏬 <b>Филиал:</b> {branch}\n"
        f"📦 <b>Наименование товара:</b> {sap_code_name}\n"
        f"📂 <b>Категория товара:</b> {category_sap_code_name}\n"
        f"💰 <b>Цена:</b> {price} ₽\n"
        f"🖼 <b>Фото:</b> <a href='{image_url}'>Просмотр</a>"
    )

    bot.send_message(chat_id=CHAT_ID, text=text, reply_markup=keyboard, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: True)
def handle_report_reason(call):
    try:
        report_id, reason_id = call.data.split(":")
        response = requests.post(
            DJANGO_API_URL,
            json={"report_id": int(report_id), "reason_id": int(reason_id)}
        )

        if response.status_code == 200:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Причина для {report_id}.\nВыбранная причина: {reason_id}"
            )
            bot.answer_callback_query(call.id, "Причина успешно обновлена!")
        else:
            bot.answer_callback_query(call.id, "Ошибка обновления причины.", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Произошла ошибка: {e}", show_alert=True)


# if __name__ == "__main__":
#     bot.polling(none_stop=True)
