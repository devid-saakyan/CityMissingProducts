import telebot
import requests
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from main.models import TelegramUser, ProductsReport, UserReview, ReviewsCategoryAnswer, ReviewsCategory
from django.db.models import Q

#BOT_TOKEN = '7933060895:AAFBfZjAYwkiNKeF138INpEI3_wCLEOziQ4'  # test
BOT_TOKEN = "7946030117:AAG_r4--uVvaLTHNKLlrIuIonaTbMr_W2Nk"
PRODUCT_REPORT_API_URL = "http://127.0.0.1:8014/api/UpdateProductReport"
REVIEW_CATEGORY_API_URL = "http://127.0.0.1:8014/api/UpdateReview/UpdateReviewCategory"
REVIEW_CATEGORY_ANSWER_API_URL = "http://127.0.0.1:8014/api/UpdateReview/UpdateReviewCategoryAnswer"

bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}


def get_active_chat_ids(branch):
    if branch:
        print(branch)
        return list(TelegramUser.objects.filter(Q(branch__name=branch) | Q(status__name='Admin')).values_list("user_id",
                                                                                                              flat=True))


def get_active_chat_ids_for_review():
    return list(
        TelegramUser.objects.filter(Q(status__name='Operator')).values_list("user_id", flat=True))


def get_active_chat_ids_for_review_answer(branch):
    return list(
        TelegramUser.objects.filter(Q(status__name='Operator2') & Q(branch__name=branch)).values_list("user_id", flat=True))


def send_report_to_telegram(sap_code_name, sap_code, price, report_id, image_url, reasons, branch, main_reason,
                            user_basket_count, stock_count, is_kilogram):
    main_reason_dict = {'Out of stock': 'Մնացորդի խնդիր', 'Product Quality': 'Որակի խնդիր',
                        'Expire Date': 'Ժամկետի խնդիր'}
    keyboard = InlineKeyboardMarkup()
    for reason in reasons:
        if reason['name'] == 'այլ':
            callback_data = f"report:{report_id}:{reason['id']}:other"
        else:
            callback_data = f"report:{report_id}:{reason['id']}:-"
        keyboard.add(InlineKeyboardButton(text=reason['name'], callback_data=callback_data))
    kilo_or_count = 'կգ' if is_kilogram is True else 'հատ'
    text = (
        f"📢 <b>Նոր վերադարձ: {main_reason_dict.get(str(main_reason))}</b>\n"
        f"🏬 <b>Մասնաճյուղ:</b> {branch}\n"
        f"📦 <b>Ապրանք:</b> {sap_code_name}\n"
        f"📂 <b>Sap Code:</b> {sap_code}\n"
        f"📦 <b>Պատվիրած քանակ:</b> {user_basket_count} {kilo_or_count}\n"
        f"📦 <b>Առկա քանակ:</b> {stock_count} {kilo_or_count}\n"
        f"💰 <b>Գին:</b> {price} ֏\n"
        f"🖼 <b>Նկար:</b> <a href='{image_url}'>Նայել</a>"
    )

    chat_ids = get_active_chat_ids(branch)
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard, parse_mode="HTML")
        except Exception as e:
            print(e)
            print(f'i cant send a message to user_id {chat_id}')


def send_review_to_telegram(order_id, rate, comment, review_id, categories, branch, order_date):
    keyboard = InlineKeyboardMarkup()
    for category in categories:
        callback_data = f"review:{review_id}:{category['id']}"
        keyboard.add(InlineKeyboardButton(text=category['name'], callback_data=callback_data))

    text = (
        f"📢 <b>Նոր գնահատական</b>\n\n"
        f"🏬 <b>Մասնաճյուղ:</b> {branch}\n"
        f"📦 <b>Պատվերի №:</b> {order_id}\n"
        f"⭐ <b>Գնահատական:</b> {rate}\n"
        f"💬 <b>Մեկնաբանություն:</b> {comment}\n"
        f"📅 <b>Պատվերի ամսաթիվը:</b> {order_date}"
    )

    #chat_ids = get_active_chat_ids(branch)
    chat_ids = get_active_chat_ids_for_review()
    print('ids', chat_ids)
    for chat_id in chat_ids:
        try:
            bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard, parse_mode="HTML")
        except:
            print(f'i cant send a message to user_id {chat_id}')


@bot.callback_query_handler(func=lambda call: call.data.startswith("report:"))
def handle_report_reason(call):
    try:
        print(call.data)
        _, report_id, reason_id, reason_name = call.data.split(":")
        if reason_name == 'other':
            bot.answer_callback_query(call.id)
            response = requests.post(
                PRODUCT_REPORT_API_URL,
                json={"report_id": int(report_id), "reason_id": int(reason_id)}
            )
            user_states[call.message.chat.id] = report_id
            print(f"User state saved: {user_states}")
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            if response.status_code == 200:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text="Խնդրում ենք նշել մեկնաբանությունը:")
            elif response.status_code == 304:
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text="Պատճառն արդեն թարմացվել է: ")
        else:
            response = requests.post(
                PRODUCT_REPORT_API_URL,
                json={"report_id": int(report_id), "reason_id": int(reason_id)}
            )
            if response.status_code == 200:
                report = ProductsReport.objects.get(id=report_id)
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"Վերադարձի պատճառը թարմացվեց:\nԸնտրված պատճառը: {report.manager_reason}"
                )
                bot.answer_callback_query(call.id, "Վերադարձի պատճառը թարմացվեց")
            elif response.status_code == 304:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"Պատճառն արդեն թարմացվել է: "
                )
            else:
                bot.answer_callback_query(call.id, "Պատճառի թարմացումը ձախողվեց։", show_alert=True)
    except Exception as e:
        print(e)
        bot.answer_callback_query(call.id, f"Սխալ է տեղի ունեցել:", show_alert=True)


@bot.message_handler(func=lambda message: message.chat.id in user_states)
def handle_comment(message):
    try:
        report_id = user_states.pop(message.chat.id, None)
        if not report_id:
            bot.send_message(chat_id=message.chat.id, text="Состояние не найдено.")
            return
        print(f"handle_comment triggered with message: {message.text} for report_id: {report_id}")
        comment = message.text
        report = ProductsReport.objects.get(id=report_id)
        report.comment = comment
        report.save()

        bot.send_message(
            chat_id=message.chat.id,
            text=f"Մեկնաբանությունը հաջողությամբ ավելացված է:\n{comment}"
        )
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        except Exception as e:
            print(f"Error deleting message: {e}")
    except Exception as e:
        print(f"Error in handle_comment: {e}")
        bot.send_message(chat_id=message.chat.id, text=f"Системная ошибка: {e}")


@bot.message_handler(func=lambda message: True)
def debug_message(message):
    print(f"Message handler triggered: {message.text} from chat {message.chat.id}")


# Обработка callback для отзывов
@bot.callback_query_handler(func=lambda call: call.data.startswith("review:"))
def handle_review_category(call):
    try:
        _, review_id, category_id = call.data.split(":")
        review = UserReview.objects.get(id=int(review_id))
        category_answers = ReviewsCategoryAnswer.objects.filter(main_category_id=int(category_id))
        keyboard = InlineKeyboardMarkup()
        for answer in category_answers:
            callback_data = f"answer:{review_id}:{answer.id}"
            keyboard.add(InlineKeyboardButton(text=answer.name, callback_data=callback_data))

        response = requests.post(
            REVIEW_CATEGORY_API_URL,
            json={"review_id": int(review_id), "category_id": int(category_id)}
        )
        type = ReviewsCategory.objects.get(id=int(category_id))
        text = (
            f"📢 <b>Նոր գնահատական: {type.name}</b>\n\n"
            f"🏬 <b>Մասնաճյուղ:</b> {review.branch}\n"
            f"📦 <b>Պատվերի №:</b> {review.order_id}\n"
            f"⭐ <b>Գնահատական:</b> {review.rate}\n"
            f"💬 <b>Մեկնաբանություն:</b> {review.comment}\n"
            f"📅 <b>Պատվերի ամսաթիվը:</b> {review.order_date}"
        )

        bot.delete_message(call.message.chat.id, call.message.message_id)
        chat_ids = get_active_chat_ids_for_review_answer(review.branch)
        print(chat_ids)
        for chat_id in chat_ids:
            try:
                bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard, parse_mode="HTML")
            except:
                print(f'i cant send a message to user_id {chat_id}')
        #bot.send_message(call.message.chat.id, text, reply_markup=keyboard, parse_mode="HTML")

    except UserReview.DoesNotExist:
        bot.answer_callback_query(call.id, "Отзыв не найден.", show_alert=True)
    except ReviewsCategoryAnswer.DoesNotExist:
        bot.answer_callback_query(call.id, "Ответы для этой категории не найдены.", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка: {str(e)}", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("answer:"))
def handle_review_answer(call):
    try:
        _, review_id, answer_id = call.data.split(":")

        review = UserReview.objects.get(id=int(review_id))
        category_answer = ReviewsCategoryAnswer.objects.get(id=int(answer_id))

        review.category_answer = category_answer
        review.save()

        response = requests.post(
            REVIEW_CATEGORY_API_URL,
            json={"review_id": int(review_id), "category_answer_id": int(answer_id)}
        )

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, f"✅ Դուք ընտրել եք: {category_answer.name}")

    except UserReview.DoesNotExist:
        bot.answer_callback_query(call.id, "Отзыв не найден.", show_alert=True)
    except ReviewsCategoryAnswer.DoesNotExist:
        bot.answer_callback_query(call.id, "Ответ не найден.", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка: {str(e)}", show_alert=True)

# import telebot
#
# BOT_TOKEN = '7933060895:AAFBfZjAYwkiNKeF138INpEI3_wCLEOziQ4'
# bot = telebot.TeleBot(BOT_TOKEN)
#
# @bot.message_handler(func=lambda message: True)
# def debug_all_messages(message):
#     print(f"Message received: {message.text} from chat {message.chat.id}")
#     bot.send_message(message.chat.id, "Ваше сообщение получено!")
#
# bot.polling(none_stop=True, interval=0)
