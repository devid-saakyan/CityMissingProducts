import os
import django
import telebot
import requests
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from main.models import TelegramUser
from django.db.models import Q

#BOT_TOKEN = '6064450479:AAFS9B4HGD7d1BEoVYL5qyUPG88otYlJzfU'
BOT_TOKEN = "7946030117:AAG_r4--uVvaLTHNKLlrIuIonaTbMr_W2Nk"
PRODUCT_REPORT_API_URL = "http://127.0.0.1:8014/api/UpdateProductReport"
REVIEW_CATEGORY_API_URL = "http://127.0.0.1:8014/api/UpdateReviewCategory"

bot = telebot.TeleBot(BOT_TOKEN)


def get_active_chat_ids(branch):
    if branch:
        print(branch)
        return list(TelegramUser.objects.filter(Q(branch__name=branch) | Q(status__name='Admin')).values_list("user_id", flat=True))


def send_report_to_telegram(sap_code_name, category_sap_code_name, price, report_id, image_url, reasons, branch):
    keyboard = InlineKeyboardMarkup()
    for reason in reasons:
        callback_data = f"report:{report_id}:{reason['id']}"
        keyboard.add(InlineKeyboardButton(text=reason['name'], callback_data=callback_data))

    text = (
        f"📢 <b>Նոր վերադարձ</b>\n"
        f"🏬 <b>Մասնաճյուղ:</b> {branch}\n"
        f"📦 <b>Ապրանք:</b> {sap_code_name}\n"
        f"📂 <b>Կատեգորիա:</b> {category_sap_code_name}\n"
        f"💰 <b>Գին:</b> {price} ֏\n"
        f"🖼 <b>Նկար:</b> <a href='{image_url}'>Նայել</a>"
    )

    chat_ids = get_active_chat_ids(branch)
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard, parse_mode="HTML")
        except:
            print(f'i cant send a message to user_id {chat_id}')


def send_review_to_telegram(order_id, rate, comment, review_id, categories, branch):
    keyboard = InlineKeyboardMarkup()
    for category in categories:
        callback_data = f"review:{review_id}:{category['id']}"
        keyboard.add(InlineKeyboardButton(text=category['name'], callback_data=callback_data))

    text = (
        f"📢 <b>Նոր գնահատական</b>\n"
        f"📦 <b>Պատվերի №:</b> {order_id}\n"
        f"⭐ <b>Գնահատական:</b> {rate}\n"
        f"💬 <b>Մեկնաբանություն:</b> {comment}"
    )

    chat_ids = get_active_chat_ids(branch)
    print(1111111111111, chat_ids)
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard, parse_mode="HTML")
        except:
            print(f'i cant send a message to user_id {chat_id}')


@bot.callback_query_handler(func=lambda call: call.data.startswith("report:"))
def handle_report_reason(call):
    try:
        _, report_id, reason_id = call.data.split(":")
        response = requests.post(
            PRODUCT_REPORT_API_URL,
            json={"report_id": int(report_id), "reason_id": int(reason_id)}
        )
        if response.status_code == 200:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Причина для возврата {report_id} обновлена.\nВыбранная причина: {reason_id}"
            )
            bot.answer_callback_query(call.id, "Причина успешно обновлена!")
        else:
            bot.answer_callback_query(call.id, "Ошибка обновления причины.", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Произошла ошибка: {e}", show_alert=True)

# Обработка callback для отзывов
@bot.callback_query_handler(func=lambda call: call.data.startswith("review:"))
def handle_review_category(call):
    try:
        _, review_id, category_id = call.data.split(":")
        response = requests.post(
            REVIEW_CATEGORY_API_URL,
            json={"review_id": int(review_id), "category_id": int(category_id)}
        )
        if response.status_code == 200:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Категория для отзыва {review_id} обновлена.\nВыбранная категория: {category_id}"
            )
            bot.answer_callback_query(call.id, "Категория успешно обновлена!")
        else:
            bot.answer_callback_query(call.id, "Ошибка обновления категории.", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Произошла ошибка: {e}", show_alert=True)
