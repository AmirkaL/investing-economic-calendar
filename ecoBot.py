import logging
from aiogram import Bot, Dispatcher, executor, types
from selen import get_today_events, get_tomorrow_events, get_week_events
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime

API_TOKEN = 'TOKEN'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

parameters = ['GDP', 'CPI', 'Unemployment Rate', 'Interest Rate Decision', 'Retail Sales']
countries = ['Albania', 'Angola', 'Argentina', 'Australia', 'Austria',
             'Azerbaijan', 'Bahrain', 'Bangladesh', 'Belgium', 'Bermuda', 'Bosnia-Herzegovina', 'Botswana', 'Brazil', 'Bulgaria', 'Canada', 'Cayman Islands', 'Chile', 'China', 'Colombia', 'Costa Rica', 'Cote D\'Ivoire', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Ecuador', 'Egypt', 'Estonia', 'Euro Zone', 'Finland', 'France', 'Germany', 'Ghana', 'Greece', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iraq', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kuwait', 'Kyrgyzstan', 'Latvia', 'Lebanon', 'Lithuania', 'Luxembourg', 'Malawi', 'Malaysia', 'Malta', 'Mauritius', 'Mexico', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Namibia', 'Netherlands', 'New Zealand', 'Nigeria', 'Norway', 'Oman', 'Pakistan', 'Palestinian Territory', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia', 'Rwanda', 'Saudi Arabia', 'Serbia', 'Singapore', 'Slovakia', 'Slovenia', 'South Africa', 'South Korea', 'Spain', 'Sri Lanka', 'Sweden', 'Switzerland', 'Taiwan', 'Tanzania', 'Thailand', 'Tunisia', 'Türkiye', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Venezuela', 'Vietnam', 'Zambia', 'Zimbabwe']


user_parameters = {}
user_countries = {}
user_pages = {}


@dp.message_handler(commands=['parm'])
async def send_parameters(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    row = []
    for parameter in parameters:
        row.append(InlineKeyboardButton(parameter, callback_data=f"param_{parameter}"))
        if len(row) == 2:
            keyboard.row(*row)
            row = []
    if row:
        keyboard.row(*row)
    keyboard.add(InlineKeyboardButton("Готово", callback_data="done"))
    await message.reply("Выберите интересующие вас параметры:", reply_markup=keyboard)



@dp.callback_query_handler(lambda query: query.data.startswith('param_'))
async def handle_parameter_callback(callback_query: types.CallbackQuery):
    parameter = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    if user_id not in user_parameters:
        user_parameters[user_id] = []
    if parameter not in user_parameters[user_id]:
        user_parameters[user_id].append(parameter)
    await bot.answer_callback_query(callback_query.id, text=f"Выбран параметр: {parameter}")


@dp.callback_query_handler(lambda query: query.data == 'done')
async def finish_selection(callback_query: types.CallbackQuery):
    await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id)



def create_country_keyboard(page_num):
    countries_per_page = 12
    start_index = (page_num - 1) * countries_per_page
    end_index = min(start_index + countries_per_page, len(countries))

    keyboard = InlineKeyboardMarkup(row_width=2)
    row = []
    for country in countries[start_index:end_index]:
        row.append(InlineKeyboardButton(country, callback_data=f"country_{country}"))
        if len(row) == 2:
            keyboard.row(*row)
            row = []
    if row:
        keyboard.row(*row)


    navigation_buttons = []
    if page_num > 1:
        navigation_buttons.append(InlineKeyboardButton("⬅️", callback_data="prev_page"))
    if end_index < len(countries):
        navigation_buttons.append(InlineKeyboardButton("➡️", callback_data="next_page"))

    if navigation_buttons:
        keyboard.add(*navigation_buttons)
        keyboard.add(InlineKeyboardButton("Готово", callback_data="done"))

    return keyboard


@dp.callback_query_handler(lambda query: query.data in ["prev_page", "next_page"])
async def process_country_pagination(callback_query: types.CallbackQuery):
    page_num = user_pages.get(callback_query.from_user.id, 1)
    if callback_query.data == "prev_page":
        page_num = max(1, page_num - 1)
    else:
        page_num += 1

    user_pages[callback_query.from_user.id] = page_num
    keyboard = create_country_keyboard(page_num)
    await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id, reply_markup=keyboard)


@dp.message_handler(commands=['country'])
async def send_countries(message: types.Message):
    keyboard = create_country_keyboard(1)
    await message.reply("Выберите интересующую вас страну:", reply_markup=keyboard)


@dp.message_handler(commands=['start'])
async def send_help(message: types.Message):

    help_message = """
    Для начала установите параметры событий и параметры страны!
    
    Список доступных команд:
    /country - Выбор параметров страны
    /parm - Выбор параметров событий
    /today - События на сегодня
    /tomorrow - События на завтра
    /week - События на неделю
    /list - Просмотр выбранных параметров
    /remove - Удаление параметров
    """
    await message.reply(help_message)

def filter_events(events, user_id):
    filtered_events = []
    for event in events:
        if event['event'] in user_parameters[user_id]:
            filtered_events.append(event)
    return filtered_events


@dp.message_handler(commands=['today'])
async def send_today_events(message: types.Message):
    chat_id = message.chat.id
    event_types = user_parameters.get(message.from_user.id, [])
    countries = user_countries.get(message.from_user.id, [])
    events = get_today_events(event_types, countries, chat_id)

    if not events:
        await message.answer("Событий с заданными параметрами не найдено.")
    else:
        event_message = ""
        for event in events:
            event_message += f"Currency: {event['currency']}\nEvent: {event['event']}\nTime: {event['time']}\nCountry: {event['country']}\n"
            event_message += f"Actual Value: {event['actual_value']}\nForecast Value: {event['forecast_value']}\nPrevious Value: {event['previous_value']}\n\n"
        await message.answer(event_message)


@dp.message_handler(commands=['tomorrow'])
async def send_tomorrow_events(message: types.Message):
    chat_id = message.chat.id
    event_types = user_parameters.get(message.from_user.id, [])
    countries = user_countries.get(message.from_user.id, [])
    events = get_tomorrow_events(event_types, countries, chat_id)

    if not events:
        await message.answer("Событий с заданными параметрами не найдено.")
    else:
        event_message = ""
        for event in events:
            event_message += f"Currency: {event['currency']}\nEvent: {event['event']}\nTime: {event['time']}\nCountry: {event['country']}\n"
            event_message += f"Actual Value: {event['actual_value']}\nForecast Value: {event['forecast_value']}\nPrevious Value: {event['previous_value']}\n\n"
        await message.answer(event_message)

@dp.message_handler(commands=['week'])
async def send_tomorrow_events(message: types.Message):
    chat_id = message.chat.id
    event_types = user_parameters.get(message.from_user.id, [])
    countries = user_countries.get(message.from_user.id, [])
    events = get_week_events(event_types, countries, chat_id)

    if not events:
        await message.answer("Событий с заданными параметрами не найдено.")
    else:
        event_message = ""
        for event in events:
            event_message += f"Date: {event['date']}\nCurrency: {event['currency']}\nEvent: {event['event']}\nTime: {event['time']}\nCountry: {event['country']}"
            event_message += f"Actual Value: {event['actual_value']}\nForecast Value: {event['forecast_value']}\nPrevious Value: {event['previous_value']}\n\n"
        await message.answer(event_message)


@dp.message_handler(commands=['remove'])
async def remove_parameter(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_parameters:
        del user_parameters[user_id]
    if user_id in user_countries:
        del user_countries[user_id]
    await message.reply("Все параметры успешно сброшены.")


@dp.message_handler(commands=['list'])
async def list_parameters(message: types.Message):
    user_id = message.from_user.id

    if user_id in user_parameters or user_id in user_countries:
        parameters_list = ", ".join(user_parameters.get(user_id, []))
        parameters_country = ", ".join(user_countries.get(user_id, []))

        await message.reply(f"Выбранные параметры:\n\nСобытия: {parameters_list} \nСтраны: {parameters_country}")
    else:
        await message.reply("Список выбранных параметров пуст.")


@dp.callback_query_handler(lambda query: query.data.startswith('param_'))
async def process_event_parameter(callback_query: types.CallbackQuery):
    parameter = callback_query.data.replace('param_', '')
    user_id = callback_query.from_user.id
    if user_id not in user_parameters:
        user_parameters[user_id] = []
    if parameter not in user_parameters[user_id]:
        user_parameters[user_id].append(parameter)
    await bot.send_message(callback_query.from_user.id, f"Выбран параметр события: {parameter}")

@dp.callback_query_handler(lambda query: query.data.startswith('country_'))
async def process_country_parameter(callback_query: types.CallbackQuery):
    country = callback_query.data.replace('country_', '')
    user_id = callback_query.from_user.id
    if user_id not in user_countries:
        user_countries[user_id] = []
    if country not in user_countries[user_id]:
        user_countries[user_id].append(country)
    await bot.answer_callback_query(callback_query.id, text=f"Выбрана страна: {country}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
