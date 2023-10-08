from telegram import Update
from telegram.ext import *
import threading
import notification_handler
import secrets
import testers
import service
from telegram import *
from telegram.ext import *
import abbreviation
from dao import *
from datetime import datetime, timedelta


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if not testers.is_allow(update.message.chat_id):
    #     await update.message.reply_text("Access denied")
    #     return
    if not dao.is_available():
        await update.message.reply_text("Ошибка подключения к базе данных, попробуйте позже")
        return
    if dao.get(update.message.chat_id) is not None:
        dao.delete(update.message.chat_id)
        await select_faculty(update, context)
        return

    await select_faculty(update, context)


async def select_faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard_buttons = [[]]
    if service.getFaculties() == "error":
        await update.message.reply_text(text="На сервере ведутся технические работы, попробуйте позже", reply_markup=None)
        return
    for faculty in service.getFaculties():
        keyboard_buttons.append([InlineKeyboardButton(text=abbreviation.abbreviation(faculty),
                                                      callback_data="1" + abbreviation.abbreviation(faculty))])

    markup = InlineKeyboardMarkup(keyboard_buttons)
    await update.message.reply_text(text="Выберите факультет/направление:", reply_markup=markup)


async def select_group(faculty: str, update: Update):
    query = update.callback_query
    await query.answer()
    keyboard_buttons = [[]]
    count_columns = 2
    if service.getGroupsByFaculty(faculty) == "error":
        await query.edit_message_text("На сервере ведутся технические работы, попробуйте позже")
        return
    groups = service.getGroupsByFaculty(faculty)[:76]
    for i in range(0, int(len(groups) / count_columns)):
        row = []
        for j in range(0, count_columns):
            row.append(InlineKeyboardButton(
                text=groups[i * count_columns + j],
                callback_data="2" + groups[i * count_columns + j]
            ))
        keyboard_buttons.append(row)
    if len(groups) % 2 != 0:
        keyboard_buttons.append([InlineKeyboardButton(text=groups[::-1][0], callback_data="2" + groups[::-1][0])])
    keyboard_buttons.append([InlineKeyboardButton(text="Назад", callback_data="2cancel")])
    markup = InlineKeyboardMarkup(keyboard_buttons)
    await query.edit_message_text(text=f"Выберите группу", reply_markup=markup)


async def handle_pressing_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data[0] == "1":
        await select_group(query.data.replace("1", ""), update)
        return

    if query.data == "2cancel":
        keyboard_buttons = [[]]
        if service.getFaculties() == "error":
            await query.edit_message_text("На сервере ведутся технические работы, попробуйте позже")
            return
        for faculty in service.getFaculties():
            keyboard_buttons.append([InlineKeyboardButton(text=abbreviation.abbreviation(faculty),
                                                          callback_data="1" + abbreviation.abbreviation(faculty))])

        markup = InlineKeyboardMarkup(keyboard_buttons)
        await query.edit_message_text(text="Выберите факультет/направление", reply_markup=markup)
        return

    if query.data[0] == "2":
        if not dao.is_available():
            await update.callback_query.edit_message_text("Ошибка подключения к базе данных, попробуйте позже")
            return
        if dao.get(query.message.chat_id) is not None:
            dao.delete(query.message.chat_id)
            await save_group(update.callback_query.message.chat_id, query.data, update, context)
            return
        await save_group(update.callback_query.message.chat_id, query.data, update, context)
        return

    if query.data[0] == "3":
        await get_timetable_by_day(update, context, query.data, update.callback_query.message.chat_id)
        return

    await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")


dao = DatabaseDao()


async def get_timetable_by_day(update: Update, context: ContextTypes.DEFAULT_TYPE, day, chat_id):
    match day:
        case "3today":
            if not dao.is_available():
                await update.callback_query.edit_message_text("Ошибка подключения к базе данных, попробуйте позже")
                return
            if dao.get(update.callback_query.message.chat_id) is None:
                await update.callback_query.edit_message_text("Сначала выберите группу")
                return
            day = datetime.date(datetime.today() + timedelta(hours=3))
            day = day.strftime("%d.%m.%Y")
            group_name = dao.get(chat_id)
            group_name = group_name[1:]
            if service.getFaculties() == "error":
                await update.callback_query.edit_message_text("На сервере ведутся технические работы, попробуйте позже")
                return
            timetable = service.get_timetable_by_day(group_name, day)
            image = service.get_image_by_day(timetable)
            query = update.callback_query
            await query.answer()
            await query.delete_message()
            await bot.send_photo(query.message.chat_id, image)

        case "3tomorrow":
            if not dao.is_available():
                await update.callback_query.edit_message_text("Ошибка подключения к базе данных, попробуйте позже")
                return
            if dao.get(update.callback_query.message.chat_id) is None:
                await update.callback_query.edit_message_text("Сначала выберите группу")
                return
            day = datetime.date(datetime.today() + timedelta(days=1, hours=3))
            day = day.strftime("%d.%m.%Y")
            group_name = dao.get(chat_id)
            group_name = group_name[1:]
            if service.getFaculties() == "error":
                await update.callback_query.edit_message_text("На сервере ведутся технические работы, попробуйте позже")
                return
            timetable = service.get_timetable_by_day(group_name, day)
            image = service.get_image_by_day(timetable)
            query = update.callback_query
            await query.answer()
            await query.delete_message()
            await bot.send_photo(query.message.chat_id, image)

        case "3current_week":
            if not dao.is_available():
                await update.callback_query.edit_message_text("Ошибка подключения к базе данных, попробуйте позже")
                return
            if dao.get(update.callback_query.message.chat_id) is None:
                await update.callback_query.edit_message_text("Сначала выберите группу")
                return
            start_of_week = service.DateManager().get_start_of_week(datetime.date(datetime.today()+timedelta(hours=3)).strftime("%d.%m.%Y"))
            end_of_week = service.DateManager().get_end_of_week(datetime.date(datetime.today()+timedelta(hours=3)).strftime("%d.%m.%Y"))
            group_name = dao.get(chat_id)
            group_name = group_name[1:]
            if service.getFaculties() == "error":
                await update.callback_query.edit_message_text("На сервере ведутся технические работы, попробуйте позже")
                return
            week = service.get_timetable_by_days(group_name, start_of_week, end_of_week)
            image = service.get_image_by_6_days(week)
            query = update.callback_query
            await query.answer()
            await query.delete_message()
            await bot.send_photo(query.message.chat_id, image)

        case "3next_week":
            if not dao.is_available():
                await update.callback_query.edit_message_text("Ошибка подключения к базе данных, попробуйте позже")
                return
            if dao.get(update.callback_query.message.chat_id) is None:
                await update.callback_query.edit_message_text("Сначала выберите группу")
                return
            start_of_week = service.DateManager().get_start_of_week(
                datetime.date(datetime.today() + timedelta(days=7,hours=3)).strftime("%d.%m.%Y"))
            end_of_week = service.DateManager().get_end_of_week(
                datetime.date(datetime.today() + timedelta(days=7, hours=3)).strftime("%d.%m.%Y"))
            group_name = dao.get(chat_id)
            group_name = group_name[1:]
            if service.getFaculties() == "error":
                await update.callback_query.edit_message_text("На сервере ведутся технические работы, попробуйте позже")
                return
            week = service.get_timetable_by_days(group_name, start_of_week, end_of_week)
            image = service.get_image_by_6_days(week)
            query = update.callback_query
            await query.answer()
            await query.delete_message()
            await bot.send_photo(query.message.chat_id, image)


async def group_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if not testers.is_allow(update.message.chat_id):
    #     await update.message.reply_text("Access denied")
    #     return
    if not dao.is_available():
        await update.message.reply_text("Ошибка подключения к базе данных, попробуйте позже")
        return
    await bot.set_my_commands([])
    await select_faculty(update, context)
    dao.delete(update.message.chat_id)


async def save_group(chat_id, group, update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not dao.is_available():
        await update.callback_query.edit_message_text("Ошибка подключения к базе данных, попробуйте позже")
        return
    await bot.set_my_commands([BotCommand(command="get_timetable", description="Получить расписание"),
                               BotCommand(command="change_group", description="Изменить группу")])
    dao.save(chat_id, group, update.callback_query.from_user.username, update.callback_query.from_user.first_name)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Ваш выбор успешно сохранен\n"
                                       "(Если не появилось меню, введите \"/\" в поле для ввода)")


async def get_timetable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # if not testers.is_allow(update.message.chat_id):
    #     await update.message.reply_text("Access denied")
    #     return
    if not dao.is_available():
        await update.message.reply_text("Ошибка подключения к базе данных, попробуйте позже")
        return
    if dao.get(update.message.chat_id) is None:
        await update.message.reply_text(text="Сначала выберите группу")
        return
    keyboard_buttons = [
        [InlineKeyboardButton(text="Сегодня", callback_data="3today")],
        [InlineKeyboardButton(text="Завтра", callback_data="3tomorrow")],
        [InlineKeyboardButton(text="Текущая неделя", callback_data="3current_week")],
        [InlineKeyboardButton(text="Следующая неделя", callback_data="3next_week")]
    ]
    await update.message.reply_text(text="Выберите", reply_markup=InlineKeyboardMarkup(keyboard_buttons))


bot = Bot(token=secrets.TOKEN)


def main():
    thread = threading.Thread(target=notification_handler.task_observer)
    thread.start()
    print("Starting...")
    app = Application.builder().token(secrets.TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler("get_timetable", get_timetable))
    app.add_handler(CommandHandler("change_group", group_change))
    # Queries
    app.add_handler(CallbackQueryHandler(handle_pressing_button))
    thread = threading.Thread(target=notification_handler.start_listening_port)
    thread.start()
    # Polls the bot
    print("Polling...")
    app.run_polling()


if __name__ == '__main__':
    main()
