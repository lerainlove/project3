import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Weather import make_query, summary_daily, summary_hourly

API_TOKEN = open("data/API_KEY.txt").read()

# Инициализируем бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Сохраняем данные пользователя
user_data = {}

# Создаем роутер
router = Router()
dp.include_router(router)


# Обработка команды /start
@router.message(Command("start"))
async def send_greeting(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}!\n\n" + open("data/start.txt", encoding="UTF-8").read())


# Обработка команды /help
@router.message(Command("help"))
async def send_help(message: types.Message):
    await message.answer(open("data/help.txt", encoding="UTF-8").read())


# Обработка команды /weather
@router.message(Command("weather"))
async def ask_coordinates(message: types.Message):
    user_data[message.from_user.id] = {}  # Инициализируем место в словаре для точек пользователя
    await message.answer("Введите координаты широты и долготы начальной точки через пробел:")


# Обработка всех текстовых сообщений
@router.message()
async def process_coordinates(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        await message.answer("Чтобы посмотреть список доступных команд, нажми /help")
        return  # Если пользователь отправил текст, не нажав /weather

    if 'start_latitude' not in user_data[user_id] or 'start_longitude' not in user_data[user_id]:
        user_data[user_id]['start_latitude'] = message.text.split()[0]
        user_data[user_id]['start_longitude'] = message.text.split()[1]
        await message.reply("Введите координаты широты и долготы конечной точки через пробел:")
    elif 'finish_latitude' not in user_data[user_id] or 'finish_longitude' not in user_data[user_id]:
        user_data[user_id]['finish_latitude'] = message.text.split()[0]
        user_data[user_id]['finish_longitude'] = message.text.split()[1]

        # Получаем данные для дальнейшей обработки
        start_lat = user_data[user_id]['start_latitude']
        start_lon = user_data[user_id]['start_longitude']
        finish_lat = user_data[user_id]['finish_latitude']
        finish_lon = user_data[user_id]['finish_longitude']


        button1 = InlineKeyboardButton(text="Да", callback_data='yes')
        button2 = InlineKeyboardButton(text="Нет", callback_data='no')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1], [button2]])

        # Выводим пользователю сообщение с проверкой корректности введенных данных
        await message.answer(
            f"Начальная точка: Широта: {start_lat}, Долгота: {start_lon}\n"
            f"Конечная точка: Широта: {finish_lat}, Долгота: {finish_lon}\n"
            "Данные введены корректно?", reply_markup= keyboard
        )


# Проверка плохих случаев запроса
def bad_request(forecast_start, forecast_finish):
    if isinstance(forecast_start, int) or isinstance(forecast_finish, int):
        if forecast_start == 503 or forecast_finish == 503:
            return "Превышен допустимый лимит запросов, попробуйте еще раз завтра"
        elif forecast_start == 400 or forecast_finish == 400:
            return "Неверно введены координаты, широта должна быть числом от -90 до 90, долгота должна быть числом от -180 до 180. Числа должны вводиться через пробел.\n\nВведите координаты начальной точки или нажмите /help"
        else:
            return "Технические неполадки. Попробуйте еще раз.\n\nВведите координаты начальной точки через пробел."

    if forecast_start is None or forecast_finish is None:
        return "Нет данных по запрашиваемым точкам, проверьте корректность места и повторите попытку. Нажмите /weather для продолжения"

    return ""

# правильная словоформа слова "час"
def format_hour(n):
    if n == 1: return "час"
    elif n in[2,3,4]: return "часа"
    return "часов"

# правильная словоформа слова "день"
def format_day(n):
    if n == 1: return "день"
    elif n in[2,3,4]: return "дня"
    return "дней"


# Обработка запроса к API AccuWeather
@router.callback_query(lambda c: c.data.startswith('time_'))
async def process_time_option(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id

    # Обработка временного интервала 3 часа
    if callback_query.data == "time_3_hours":
        forecast_start = make_query(user_data[user_id]['start_latitude'], user_data[user_id]['start_longitude'], hourly=True)
        forecast_finish = make_query(user_data[user_id]['finish_latitude'], user_data[user_id]['finish_longitude'], hourly=True)

        error_occurred = bad_request(forecast_start, forecast_finish)
        # В случае возникновения ошибок
        if error_occurred != "":
            await bot.send_message(user_id, error_occurred)
        else:
            link_start,link_finish = "",""

            # Получаем данные по каждому часу
            for i in range(3):
                start_result, link_st = summary_hourly(forecast_start[i])
                finish_result, link_fn = summary_hourly(forecast_finish[i])
                await bot.send_message(user_id,
                                       f"Для начальной точки через {i+1} {format_hour(i+1)}:\n{start_result}\n\nДля конечной точки через {i+1} {format_hour(i+1)}:\n{finish_result}"
                                       )
                if link_start == "":link_start,link_finish = link_st,link_fn

            await bot.send_message(user_id, f"Для более подробной информации смотрите\nДля начальной точки:{link_start}\n\nДля конечной точки:{link_finish}")

    # Обработка временного интервала 12 часов
    elif callback_query.data == "time_12_hours":
        forecast_start = make_query(user_data[user_id]['start_latitude'], user_data[user_id]['start_longitude'], hourly=True)
        forecast_finish = make_query(user_data[user_id]['finish_latitude'], user_data[user_id]['finish_longitude'], hourly=True)

        error_occurred = bad_request(forecast_start, forecast_finish)
        # В случае возникновения ошибок
        if error_occurred != "":
            await bot.send_message(user_id, error_occurred)
        else:
            link_start,link_finish = "",""
            # Получаем данные по каждым 3 часам
            for i in range(2,12,3):
                start_result, link_st = summary_hourly(forecast_start[i])
                finish_result, link_fn = summary_hourly(forecast_finish[i])
                await bot.send_message(user_id,
                                       f"Для начальной точки через {i+1} {format_hour(i+1)}:\n{start_result}\n\nДля конечной точки через {i+1} {format_hour(i+1)}:\n{finish_result}"
                                       )
                if link_start == "":link_start,link_finish = link_st,link_fn
            await bot.send_message(user_id, f"Для более подробной информации смотрите\nДля начальной точки:{link_start}\n\nДля конечной точки:{link_finish}")

    # Обработка временного интервала 5 дней
    else:
        forecast_start = make_query(user_data[user_id]['start_latitude'], user_data[user_id]['start_longitude'],
                                    daily=True)
        forecast_finish = make_query(user_data[user_id]['finish_latitude'], user_data[user_id]['finish_longitude'],
                                     daily=True)

        error_occurred = bad_request(forecast_start, forecast_finish)
        # В случае возникновения ошибок
        if error_occurred != "":
            await bot.send_message(user_id, error_occurred)
        else:
            link_start, link_finish = "", ""
            # Получаем данные по каждому дню
            for i in range(5):
                start_result, link_st = summary_daily(forecast_start[i])
                finish_result, link_fn = summary_daily(forecast_finish[i])
                await bot.send_message(user_id,
                                       f"Для начальной точки через {i+1} {format_day(i+1)}:\n{start_result}\n\nДля конечной точки через {i+1} {format_day(i+1)}:\n{finish_result}"
                                       )
                if link_start == "": link_start, link_finish = link_st, link_fn
            await bot.send_message(user_id,
                                   f"Для более подробной информации смотрите\nДля начальной точки:{link_start}\n\nДля конечной точки:{link_finish}")


# Обработка случая, когда пользователь подтвердил корректность данных
@router.callback_query(lambda c: c.data == "yes")
async def process_time_option(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    button1 = InlineKeyboardButton(text="3 часа", callback_data='time_3_hours')
    button2 = InlineKeyboardButton(text="12 часов", callback_data='time_12_hours')
    button3 = InlineKeyboardButton(text="5 дней", callback_data='time_5_days')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1], [button2], [button3]])

    await bot.send_message(callback_query.from_user.id,"Выберете временной интервал", reply_markup=keyboard)

# Обработка случая, когда пользователь не подтвердил корректность данных
@router.callback_query(lambda c: c.data == "no")
async def process_time_option(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user_data[user_id] = {}
    await bot.send_message(user_id,"Давайте начнем сначала.\n\nВведите координаты широты и долготы начальной точки через пробел:")

# Функция, которая запускает самого бота
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())