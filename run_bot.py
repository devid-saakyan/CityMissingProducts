import os
import django
import requests
import time
# Настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CityMissingProducts.settings")
django.setup()


from main.bot import bot
if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, timeout=60, interval=0)
        except requests.exceptions.ReadTimeout:
            print("ReadTimeout: Перезапуск бота...")
            time.sleep(5)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)
