from telegram import Update
from telegram.ext import *
import secrets
import testers
import service
from telegram import *
from telegram.ext import *
import abbreviation
from dao import *
from datetime import datetime, timedelta


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not testers.is_allow(update.message.chat_id):
        await update.message.reply_text("Access denied")
        return

    await select_faculty(update, context)


async def select_faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard_buttons = [[]]
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
        for faculty in service.getFaculties():
            keyboard_buttons.append([InlineKeyboardButton(text=abbreviation.abbreviation(faculty),
                                                          callback_data="1" + abbreviation.abbreviation(faculty))])

        markup = InlineKeyboardMarkup(keyboard_buttons)
        await query.edit_message_text(text="Выберите факультет/направление", reply_markup=markup)
        return

    if query.data[0] == "2":
        await save_group(update.callback_query.message.chat_id, query.data, update, context)
        return

    if query.data[0] == "3":
        await get_timetable_by_day(update, context, query.data, update.callback_query.message.chat_id)
        return

    await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")


dao = InMemoryDao()


def current_type(type, chat_id):
    match type:
        case "lec":
            type = "Лекция"
            return type
        case "prac":
            type = "Практика"
            return type
        case "exam":
            type = "Экзамен"
            return type
        case "lab":
            if (chat_id == 974335854) or (chat_id == 504728940) or (chat_id == 1258770584):
                type = "Сидим дома бляд"
                return type
            else:
                type = "Лаб. работа"
                return type
        case "hol":
            type = "Выходной"
            return type
        case "cred":
            type = "Зачет"
            return type
        case "cons":
            type = "Консультация"
            return type
        case "fepo":
            type = "ФЭПО"
            return type
        case "none":
            type = "Я хз"
            return type


async def get_timetable_by_day(update: Update, context: ContextTypes.DEFAULT_TYPE, day, chat_id):
    match day:
        case "3today":
            day = datetime.date(datetime.today())
            day = day.strftime("%d.%m.%Y")
            group_name = dao.get(chat_id)
            group_name = group_name[1:]
            text = ""
            timetable = service.get_timetable_by_day(group_name, day)
            for day in timetable["disciplines"]:
                type = day['type']
                text = text + (f"Время: {day['time']}\n"
                               f"Название: {day['name']}\n"
                               f"Преподаватель: {day['teacherName']}\n"
                               f"Аудитория: {day['audienceId']}\n"
                               f"Тип пары: {current_type(type, chat_id)}\n"
                               f"-----------------\n")

            if text == "":
                text = "Гуляйте"

            query = update.callback_query
            await query.answer()
            await query.edit_message_text(text)

        case "3tomorrow":
            day = datetime.date(datetime.today()) + timedelta(days=3)
            day = day.strftime("%d.%m.%Y")
            group_name = dao.get(chat_id)
            group_name = group_name[1:]
            text = ""
            timetable = service.get_timetable_by_day(group_name, day)
            for day in timetable["disciplines"]:
                type = day['type']
                text = text + (f"Время: {day['time']}\n"
                               f"Название: {day['name']}\n"
                               f"Преподаватель: {day['teacherName']}\n"
                               f"Аудитория: {day['audienceId']}\n"
                               f"Тип пары: {current_type(type, chat_id)}\n"
                               f"-----------------\n")

            if text == "":
                text = "Гуляйте"

            query = update.callback_query
            await query.answer()
            await query.edit_message_text(text)

        case "3current_week":
            start_of_week = service.DateManager().get_start_of_week(datetime.date(datetime.today()).strftime("%d.%m.%Y"))
            end_of_week = service.DateManager().get_end_of_week(datetime.date(datetime.today()).strftime("%d.%m.%Y"))
            group_name = dao.get(chat_id)
            group_name = group_name[1:]
            text = ""
            week = service.get_timetable_by_days(group_name, start_of_week, end_of_week)
            for day in week:
                text = text + "\n***********************\n"
                text = text + "Дата: " + day["date"] + "\n"
                for timetable in day["disciplines"]:
                    type = timetable['type']
                    text = text + (f"Время: {timetable['time']}\n"
                                   f"Название: {timetable['name']}\n"
                                   f"Преподаватель: {timetable['teacherName']}\n"
                                   f"Аудитория: {timetable['audienceId']}\n"
                                   f"Тип пары: {current_type(type, chat_id)}\n"
                                   f"----------------------\n"
                                   )

            if text == "":
                text = "Гуляйте"

            query = update.callback_query
            await query.answer()
            await query.edit_message_text(text)

        case "3next_week":
            start_of_week = service.DateManager().get_start_of_week(
                datetime.date(datetime.today() + timedelta(days=7)).strftime("%d.%m.%Y"))
            end_of_week = service.DateManager().get_end_of_week(
                datetime.date(datetime.today() + timedelta(days=7)).strftime("%d.%m.%Y"))
            group_name = dao.get(chat_id)
            group_name = group_name[1:]
            text = ""
            week = service.get_timetable_by_days(group_name, start_of_week, end_of_week)
            for day in week:
                text = text + "\n***********************\n"
                text = text + "Дата: " + day["date"] + "\n"
                for timetable in day["disciplines"]:
                    type = timetable['type']
                    text = text + (f"Время: {timetable['time']}\n"
                                   f"Название: {timetable['name']}\n"
                                   f"Преподаватель: {timetable['teacherName']}\n"
                                   f"Аудитория: {timetable['audienceId']}\n"
                                   f"Тип пары: {current_type(type, chat_id)}\n"
                                   f"----------------------\n"
                                   )

            if text == "":
                text = "Гуляйте"

            query = update.callback_query
            await query.answer()
            await query.edit_message_text(text[:4096])
            if len(text) > 4096:
                await query.message.reply_text(text[4096:])


async def group_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await bot.set_my_commands([])
    await select_faculty(update, context)
    dao.delete(update.message.chat_id)



async def save_group(chat_id, group, update: Update, context: ContextTypes.DEFAULT_TYPE):
    await bot.set_my_commands([BotCommand(command="get_timetable", description="Получить расписание"),
                               BotCommand(command="change_group", description="Изменить группу")])
    dao.save(chat_id, group)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Ваш выбор успешно сохранен\n"
                                       "(Если не появилось меню, введите \"/\" в поле для ввода)")


async def get_timetable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        dao.get(update.message.chat_id)
    except:
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

if __name__ == '__main__':
    print("Starting...")
    app = Application.builder().token(secrets.TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    # app.add_handler(CommandHandler('stop', end_command))
    app.add_handler(CommandHandler("get_timetable", get_timetable))
    app.add_handler(CommandHandler("change_group", group_change))
    # Queries
    app.add_handler(CallbackQueryHandler(handle_pressing_button))

    # Polls the bot
    print("Polling...")
    app.run_polling()
