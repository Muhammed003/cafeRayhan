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

def generate_audio_feedback(request, task_type):
    # Создаем список сообщений, основанных на типе задачи
    user_feedback = request.user.username # Extract user from the GET request, defaulting to None if not provided
    # If no user is provided, fall back to a default (for example, 'Гость')
    if user_feedback is None:
        user_feedback = "Гость"

    task_feedback = {
        "greetings": [
        f"Привет, {request.user.username}, как дела? Рад тебя видеть!",
        f"Добро пожаловать в кафе Райхан, {request.user.username}! Чем могу помочь?",
        f"Здравствуйте, {request.user.username}!",
        f"Приветствую вас в нашем кафе, {request.user.username}! Что будем делать?",
        f"Добрый день, {request.user.username}! Как приятно видеть вас снова в кафе Райхан!",
        f"Привет, {request.user.username}! Какие у вас планы на сегодня?",
        f"Добро пожаловать, {request.user.username}! Чем могу порадовать в этот день?",
        f"Здравствуйте, {request.user.username}! как ваши здоровье?",
        ],
        "after_work": [
        f"Ты отлично справилась сегодня, {request.user.username}! Мы все гордимся твоей работой!",
        f"Как всегда, ты сделала этот день лучше, {request.user.username}! Спасибо за твою упорную работу!",
        f"Ты – настоящая звезда, {request.user.username}! Отличная работа сегодня!",
        f"Твоя работа вдохновляет нас всех, {request.user.username}! Ты была потрясающей!",
        f"Ты замечательная, {request.user.username}, твои усилия не остались незамеченными! Ты потрясающая!",
        f"Твои усилия делают кафе Райхан особенным, {request.user.username}. Спасибо за всё!",
        f"Ты заслуживаешь самых лучших слов, {request.user.username}. Твой труд ценен и важен для нас!",
        f"Сегодня ты была невероятна, {request.user.username}! Мы все ценим твои усилия!",
        f"Ты сделала этот день особенно приятным, {request.user.username}. Спасибо за твою работу!",
        f"Каждый день с тобой – это удача, {request.user.username}. Ты потрясающая!"
        ],
        "best_user_feedback": [
            f"Ты на первом месте, {user_feedback}! Продолжай в том же духе, и победа будет твоя!",
            f"Ты в лидерах, {user_feedback}! Не останавливайся на достигнутом, ты можешь выиграть!",
            f"Сейчас ты на первом месте, {user_feedback}! Твои усилия замечены, продолжай двигаться вперёд!",
            f"Поздравляем, {user_feedback}! Ты на первом месте, и это только начало твоих достижений!",
            f"Ты на высоте, {user_feedback}! Продолжай так, и первое место в этом месяце будет твоим!",
            f"Сейчас ты впереди, {user_feedback}! Ты на первом месте, и это не случайность!",
            f"Молодец, {user_feedback}! Ты на первом месте! С такими темпами победа не заставит себя ждать!",
            f"Ты на лидерской позиции, {user_feedback}! Продолжай работать так же усердно, и победа будет твоей!",
            f"Ты сейчас в числе лидеров, {user_feedback}! Твои усилия впечатляют, держись крепко!",
            f"Ты на первом месте, {user_feedback}! Продолжай работать с такой же решимостью, и успех тебе обеспечен!"
        ],
        "user_late": [
            f"Ты опоздал, {user_feedback}. Это неприемлемо!",
            f"{user_feedback}, ты снова опоздал! Нужно исправляться!",
            f"Опоздание — это не нормально, {user_feedback}!",
            f"Не время для опозданий, {user_feedback}!",
            f"Ты уже опоздал, {user_feedback}, это так не должно быть!",
            f"Ты опоздал, {user_feedback}. Как говорится, 'время — деньги'.",
            f"{user_feedback}, опоздание — неуважение. 'Тот, кто опоздал, тот и виноват'.",
            f"Ты снова опоздал, {user_feedback}. 'Лучше поздно, чем никогда', но не всегда.",
            f"Опоздание — это не оправдание, {user_feedback}. 'Кто не успел, тот опоздал'.",
            f"Ты опоздал, {user_feedback}. 'Время не ждёт', не забывай об этом!",
            f"Опоздал, {user_feedback}. 'Время не зафиксируется'."

        ]
    }

    # Выбираем случайное сообщение в зависимости от типа задачи
    text = random.choice(task_feedback.get(task_type, ["Привет, как могу помочь, {request.user.username}?"]))

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