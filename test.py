import requests

# URL вашего Django API
url = "http://127.0.0.1:8000/api/UpdateReviewCategory"

# Данные для отправки
data = {
    "review_id": 1,  # Укажите существующий ID отзыва
    "category_id": 1  # Укажите существующий ID категории
}

# Отправка POST-запроса
response = requests.post(url, json=data)

# Проверка результата
if response.status_code == 200:
    print("Успешно обновлено:", response.json())
else:
    print("Ошибка:", response.status_code, response.text)
