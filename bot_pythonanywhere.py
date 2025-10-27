# -*- coding: utf-8 -*-
"""
Telegram Bot для сбора заявок - PythonAnywhere версия
"""
import sys
import asyncio
import time
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, CommandHandler, filters

# Твой токен от @BotFather для @KaifTime_Franch_bot
TOKEN = '8467184939:AAGsFjLQAHcMTfKsTAnbPTBC0YSlaQkGxpg'

# ID твоего Telegram-канала
CHAT_ID = '-1003052947504'

# Состояния пользователя
user_data = {}
completed_applications = {}
channel_message_ids = {}

# Начало (приветствие)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print(f"Получена команда /start от {update.effective_user.username} (ID: {update.effective_chat.id})")
        await update.message.reply_text(
            "Здравствуйте! Здорово, что вы решили начать свой путь к успеху:) "
            "Для начала давайте познакомимся, как вас зовут?"
        )
        user_data[update.effective_chat.id] = {"step": "waiting_name"}
    except Exception as e:
        print(f"Ошибка в start: {e}")

# Ожидание сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        print(f"Получено сообщение от {chat_id}: {update.message.text}")

        # Если пользователь не в активном сценарии, но есть завершенная заявка
        if chat_id not in user_data:
            if chat_id in completed_applications:
                # Добавляем сообщение к завершенной заявке
                completed_applications[chat_id]["additional_messages"].append(update.message.text)
                print(f"Добавлено дополнительное сообщение от {chat_id}: {update.message.text}")

                # Редактируем существующее сообщение в канале
                try:
                    additional_text = "\n".join([f"• {msg}" for msg in completed_applications[chat_id]["additional_messages"]])
                    message_text = (
                        f"Новая заявка!\n"
                        f"Имя: {completed_applications[chat_id]['name']}\n"
                        f"Город: {completed_applications[chat_id]['city']}\n"
                        f"Телефон: {completed_applications[chat_id]['phone']}\n"
                        f"Время: {completed_applications[chat_id]['time']}\n"
                        f"Дополнительные сообщения:\n{additional_text}"
                    )

                    # Редактируем сообщение, если есть его ID
                    if chat_id in channel_message_ids:
                        await context.bot.edit_message_text(
                            chat_id=CHAT_ID,
                            message_id=channel_message_ids[chat_id],
                            text=message_text
                        )
                        print(f"Заявка отредактирована в канале {CHAT_ID}")
                    else:
                        # Если ID сообщения не найден, отправляем новое
                        sent_message = await context.bot.send_message(CHAT_ID, message_text)
                        channel_message_ids[chat_id] = sent_message.message_id
                        print(f"Новая заявка отправлена в канал {CHAT_ID}")
                except Exception as e:
                    print(f"Ошибка редактирования заявки в канале: {e}")

            print(f"Сценарий для {chat_id} не активен, отправляю финальное сообщение")
            await update.message.reply_text(
                "Спасибо, мы уже получили вашу заявку, в скором времени свяжемся с вами. "
                "Если хотите что-то дополнить или исправить, просто напишите снизу дополнительную информацию, которую нам надо знать"
            )
            return

        step = user_data[chat_id]["step"]

        if step == "waiting_name":
            user_data[chat_id]["name"] = update.message.text
            print(f"Сохранено имя: {update.message.text}")
            await update.message.reply_text(
                f"Приятно познакомиться, {update.message.text}. "
                "Подскажите в каком городе хотели бы открыть свое дело?"
            )
            user_data[chat_id]["step"] = "waiting_city"

        elif step == "waiting_city":
            user_data[chat_id]["city"] = update.message.text
            print(f"Сохранён город: {update.message.text}")
            await update.message.reply_text(
                f"{update.message.text}? Бывали там, красивый город! "
                f"К сожалению, мы не можем приехать в славный город {update.message.text} и встретиться, "
                "давайте сделаем так, оставьте свой номер и мы с вами свяжемся, чтобы обсудить наше совместное дело."
            )
            user_data[chat_id]["step"] = "waiting_phone"

        elif step == "waiting_phone":
            user_data[chat_id]["phone"] = update.message.text
            print(f"Сохранён номер: {update.message.text}")
            # Отправка данных в канал
            try:
                sent_message = await context.bot.send_message(
                    CHAT_ID,
                    f"Новая заявка!\n"
                    f"Имя: {user_data[chat_id]['name']}\n"
                    f"Город: {user_data[chat_id]['city']}\n"
                    f"Телефон: {user_data[chat_id]['phone']}\n"
                    f"Время: {update.message.date}"
                )
                # Сохраняем ID сообщения для последующего редактирования
                channel_message_ids[chat_id] = sent_message.message_id
                print(f"Заявка отправлена в канал {CHAT_ID}, ID сообщения: {sent_message.message_id}")
            except Exception as e:
                print(f"Ошибка отправки в канал: {e}")

            # Сохраняем данные заявки для сбора дополнительных сообщений
            completed_applications[chat_id] = {
                "name": user_data[chat_id]["name"],
                "city": user_data[chat_id]["city"],
                "phone": user_data[chat_id]["phone"],
                "time": update.message.date,
                "additional_messages": []
            }

            # Отправляем финальное сообщение
            await update.message.reply_text(
                "KAIF! Ждите звонка, в скором времени свяжемся с вами. "
                "Если хотите что-то дополнить или исправить, просто напишите снизу дополнительную информацию, которую нам надо знать."
            )

            # Очищаем данные после завершения сценария
            del user_data[chat_id]
    except Exception as e:
        print(f"Ошибка в handle_message: {e}")

# Запуск бота
def main():
    try:
        print("Запуск бота @KaifTime_Franch_bot...")
        print(f"Время запуска: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Бот запущен, ожидаю команду /start")
        print("Для остановки нажмите Ctrl+C")
        
        # Запуск в режиме polling с обработкой ошибок
        application.run_polling(
            drop_pending_updates=True,
            close_loop=False
        )
    except KeyboardInterrupt:
        print("Бот остановлен пользователем")
    except Exception as e:
        print(f"Критическая ошибка при запуске бота: {e}")
        print("Попытка перезапуска через 5 секунд...")
        time.sleep(5)
        main()  # Рекурсивный перезапуск

if __name__ == '__main__':
    main()


