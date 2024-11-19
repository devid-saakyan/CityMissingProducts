import os
import django

# Настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CityMissingProducts.settings")
django.setup()


from main.bot import bot
if __name__ == "__main__":
    bot.polling(none_stop=True)
