import os
import sys
import django
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Путь до корня проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Указываем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codd.settings')

# Настраиваем Django
django.setup()

from main.models import Incident  # Импортируем модель

# Состояния разговора
WAITING_PHOTO, WAITING_STREET, WAITING_DESCRIPTION = range(3)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Сообщить о происшествии"]]
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )

# Сообщить о происшествии
async def report_incident(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пожалуйста, отправьте фотографию происшествия.")
    return WAITING_PHOTO

# Получение фотографии
async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()

    # Сохраняем фото в папку media/incidents/
    photo_path = os.path.join('media', 'incidents', f"{photo.file_id}.jpg")
    os.makedirs(os.path.dirname(photo_path), exist_ok=True)
    await photo_file.download_to_drive(photo_path)

    # Сохраняем путь к фото в user_data для дальнейшего использования
    context.user_data['photo_path'] = photo_path
    await update.message.reply_text("Теперь укажите улицу, где произошло событие.")
    return WAITING_STREET

# Получение улицы
async def receive_street(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['street'] = update.message.text
    await update.message.reply_text("Опишите происшествие:")
    return WAITING_DESCRIPTION

# Получение описания
from asgiref.sync import sync_to_async

async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['description'] = update.message.text

    # Сохранение в базу данных с использованием sync_to_async
    await sync_to_async(Incident.objects.create)(
        user_id=update.message.from_user.id,
        street=context.user_data['street'],
        description=context.user_data['description'],
        photo=f'incidents/{os.path.basename(context.user_data["photo_path"])}'  # Сохраняем только имя файла, путь будет рассчитываться автоматически
    )

    await update.message.reply_text("Ваше сообщение сохранено. Спасибо!")
    return ConversationHandler.END

# Основная функция
def main():
    application = Application.builder().token("7740302577:AAHb8hPCiIa6LdgRyZlgsAdtquKXp7W4y38").build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Сообщить о происшествии$"), report_incident)],
        states={
            WAITING_PHOTO: [MessageHandler(filters.PHOTO, receive_photo)],
            WAITING_STREET: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_street)],
            WAITING_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
