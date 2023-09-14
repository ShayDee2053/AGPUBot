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
    querry = update.callback_query
    await querry.answer()
    keyboard_buttons = [[]]
    count_columns = 2
    for i in range(0, int(len(service.getGroupsByFaculty(faculty)) / count_columns)):
        row = []
        for j in range(0, count_columns):
            row.append(InlineKeyboardButton(
                text=service.getGroupsByFaculty(faculty)[i * count_columns + j],
                callback_data="2" + service.getGroupsByFaculty(faculty)[i * count_columns + j]
            ))
        keyboard_buttons.append(row)
    keyboard_buttons.append([InlineKeyboardButton(text="Назад", callback_data="2cancel")])
    markup = InlineKeyboardMarkup(keyboard_buttons)
    await querry.edit_message_text(text=f"Выберите группу", reply_markup=markup)


async def handle_pressing_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data[0] == "1":
        await select_group(query.data.replace("1", ""), update)
        return

    if query.data[0] == "2":
        await save_group(update.callback_query.message.chat_id, query.data, update, context)
        return

    if query.data[0] == "3":
        await get_timetable_by_day(update, context, query.data, update.callback_query.message.chat_id)
        return

    if query.data == "2cancel":
        keyboard_buttons = [[]]
        for faculty in service.getFaculties():
            keyboard_buttons.append([InlineKeyboardButton(text=abbreviation.abbreviation(faculty),
                                                      callback_data="1" + abbreviation.abbreviation(faculty))])

        markup = InlineKeyboardMarkup(keyboard_buttons)
        await query.edit_message_text(text="Выберите факультет/направление", reply_markup=markup)
        return

    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")

dao = InMemoryDao()


async def get_timetable_by_day(update: Update, context: ContextTypes.DEFAULT_TYPE, day, chat_id):
    match day:
        case "3today":
            day = datetime.date(datetime.today())
            day = day.strftime("%d.%m.%Y")
            group_name = dao.get(chat_id)
            group_name = group_name[1:]
            text = ""
            timetable = service.get_timetable_by_day(group_name, day)
            for discipline in timetable["disciplines"]:
                type = discipline['type']
                match type:
                    case "lec":
                        type = "Лекция"
                    case "prac":
                        type = "Практика"
                    case "exam":
                        type = "Экзамен"
                    case "lab":
                        if chat_id == 974335854 or chat_id == 504728940:
                            type = "Сидим дома бляд"
                        else:
                            type = "Лаб. работа"
                    case "hol":
                        type = "Выходной"
                    case "cred":
                        type = "Зачет"
                    case "cons":
                        type = "Консультация"
                    case "fepo":
                        type = "ФЭПО"
                    case "none":
                        type = "Я хз"

                text = text + (f"Время: {discipline['time']}\n"
                               f"Название: {discipline['name']}\n"
                               f"Преподаватель: {discipline['teacherName']}\n"
                               f"Аудитория: {discipline['audienceId']}\n"
                               f"Тип пары: {type}\n"
                               f"-----------------\n")

            query = update.callback_query
            await query.answer()
            await query.edit_message_text(text)

        case "3tomorrow":
            day = datetime.date(datetime.today()) + timedelta(days=1)
            day = day.strftime("%d.%m.%Y")
            group_name = dao.get(chat_id)
            group_name = group_name[1:]
            text = ""
            timetable = service.get_timetable_by_day(group_name, day)
            for discipline in timetable["disciplines"]:
                type = discipline['type']
                match type:
                    case "lec":
                        type = "Лекция"
                    case "prac":
                        type = "Практика"
                    case "exam":
                        type = "Экзамен"
                    case "lab":
                        if chat_id == 974335854 or chat_id == 504728940:
                            type = "Сидим дома бляд"
                        else:
                            type = "Лаб. работа"
                    case "hol":
                        type = "Выходной"
                    case "cred":
                        type = "Зачет"
                    case "cons":
                        type = "Консультация"
                    case "fepo":
                        type = "ФЭПО"
                    case "none":
                        type = "Я хз"

                text = text + (f"Время: {discipline['time']}\n"
                               f"Название: {discipline['name']}\n"
                               f"Преподаватель: {discipline['teacherName']}\n"
                               f"Аудитория: {discipline['audienceId']}\n"
                               f"Тип пары: {type}\n"
                               f"-----------------\n")

            query = update.callback_query
            await query.answer()
            await query.edit_message_text(text)


async def save_group(chat_id, group, update: Update, context: ContextTypes.DEFAULT_TYPE):
    await bot.set_my_commands([BotCommand(command="get_timetable", description="Получить расписание"),
                               BotCommand(command="change_group", description="Изменить группу")])
    dao.save(chat_id, group)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Ваш выбор успешно сохранен\n"
                                       "(Если не появилось меню, введите \"/\" в поле для ввода)")


async def get_timetable(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    # Queries
    app.add_handler(CallbackQueryHandler(handle_pressing_button))

    # Polls the bot
    print("Polling...")
    app.run_polling()
