from apps.rayhan.homePage.services.robot_data import collect_today_data
from django.http import JsonResponse
from gtts import gTTS
import os
import random
from django.conf import settings
import threading
import time

def delete_temp_file(file_path):
    """Функция для удаления временного файла через 5 секунд."""
    # Ждем 5 секунд перед удалением
    time.sleep(5)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Файл {file_path} удален.")
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")

def generate_audio_report(request):
    # Создаем список сообщений, основанных на типе задачи
    user_feedback = request.user # Extract user from the GET request, defaulting to None if not provided
    # If no user is provided, fall back to a default (for example, 'Гость')
    if user_feedback is None:
        user_feedback = "Гость"

    # Выбираем случайное сообщение в зависимости от типа задачи
    text = collect_today_data(request)
    # Генерация аудио с использованием gTTS
    tts = gTTS(text, lang='ru', slow=False)

    # Создаем уникальное имя файла для аудио
    audio_filename = f"feedback_{os.urandom(8).hex()}.mp3"

    # Путь для сохранения аудиофайла в MEDIA_ROOT
    audio_file_path = os.path.join(settings.MEDIA_ROOT, audio_filename)

    # Сохраняем файл в MEDIA_ROOT
    tts.save(audio_file_path)

    # Путь, по которому можно будет обратиться к файлу через браузер
    audio_url = f"/media/{audio_filename}"

    # Создаем JsonResponse
    response = JsonResponse({'audio_url': audio_url})

    # Удаляем временный файл через 5 секунд в фоновом потоке
    threading.Thread(target=delete_temp_file, args=(audio_file_path,)).start()

    # Возвращаем ответ
    return response