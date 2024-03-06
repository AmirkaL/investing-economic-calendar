from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import asyncio

import datetime

def parse_event_time(time_str):
    if "min" in time_str:
        minutes = int(time_str.split()[0])
        event_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    else:
        event_time = datetime.datetime.strptime(time_str, "%H:%M")
        event_time = event_time.replace(year=datetime.datetime.now().year,
                                        month=datetime.datetime.now().month,
                                        day=datetime.datetime.now().day)
    return event_time


async def schedule_notification(chat_id, event_time, event_description):
    from ecoBot import bot
    notification_time = event_time - datetime.timedelta(minutes=15)
    current_time = datetime.datetime.now()
    time_difference = (notification_time - current_time).total_seconds()

    if time_difference > 0:
        await asyncio.sleep(time_difference)
        await bot.send_message(chat_id, f"Через 15 минут начнется событие: {event_description}")
    else:
        print("Уведомление не отправлено: событие уже началось или прошло")

def get_today_events(event_types, countries, chat_id):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "C:/Users/hogan/Downloads/chrome-win64/chrome-win64/chrome.exe"
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.investing.com/economic-calendar/")

    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "economicCurrentTime")))
    button.click()

    moscow_timezone = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "liTz18")))
    moscow_timezone.click()
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find_all(class_="js-event-item")

    result = []

    for bl in table:
        event_time_str = bl.find(class_="first left time js-time").text
        event_time = parse_event_time(event_time_str)

        event_currency = bl.find(class_="left flagCur noWrap").text.split(' ')
        intensity = bl.find_all(class_="left textNum sentiment noWrap")
        event_country = bl.find(class_="left flagCur noWrap").find('span')['title']

        event_description = ""
        event_element = bl.find(class_='left event').a
        if event_element:
            event_description = event_element.text.strip()

        if event_country in countries and any(param in event_description for param in event_types):
            event_id = event_currency[1] + '_' + event_time_str

            event_intensity = {"1": 0, "2": 0, "3": 0, "priority": 0}

            for intence in intensity:
                _true = intence.find_all(class_="grayFullBullishIcon")
                _false = intence.find_all(class_="grayEmptyBullishIcon")

                if len(_true) == 1:
                    event_intensity['1'] += 1
                    event_intensity['priority'] = 1

                elif len(_true) == 2:
                    event_intensity['2'] += 1
                    event_intensity['priority'] = 2

                elif len(_true) == 3:
                    event_intensity['3'] += 1
                    event_intensity['priority'] = 3

            actual_value_tag = bl.find('td', id=lambda x: x and x.startswith('eventActual'))
            forecast_value_tag = bl.find(class_="fore")
            previous_value_tag = bl.find(class_="prev")

            actual_value = actual_value_tag.text.strip() if actual_value_tag else "Нет данных"
            forecast_value = forecast_value_tag.text.strip() if forecast_value_tag else "Нет данных"
            previous_value = previous_value_tag.text.strip() if previous_value_tag else "Нет данных"

            event_data = {
                'currency': event_currency[1],
                'event': event_description,
                'time': event_time,
                'intensity': event_intensity,
                'country': event_country,
                'actual_value': actual_value,
                'forecast_value': forecast_value,
                'previous_value': previous_value
            }

            result.append(event_data)

            asyncio.create_task(schedule_notification(chat_id, event_time, event_description))

    driver.quit()
    return result



def get_tomorrow_events(event_types, countries, chat_id):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "C:/Users/hogan/Downloads/chrome-win64/chrome-win64/chrome.exe"
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.investing.com/economic-calendar/")

    tomorrow_tab = driver.find_element(By.ID, "timeFrame_tomorrow")
    tomorrow_tab.click()

    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "economicCurrentTime")))
    button.click()

    moscow_timezone = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "liTz18")))
    moscow_timezone.click()
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.find_all(class_="js-event-item")

    result = []

    for bl in table:
        event_time_str = bl.find(class_="first left time js-time").text
        event_time = parse_event_time(event_time_str)

        event_time = bl.find(class_="first left time js-time").text
        event_currency = bl.find(class_="left flagCur noWrap").text.split(' ')
        intensity = bl.find_all(class_="left textNum sentiment noWrap")
        event_country = bl.find(class_="left flagCur noWrap").find('span')['title']

        event_description = ""
        event_element = bl.find(class_='left event').a
        if event_element:
            event_description = event_element.text.strip()

        if event_country in countries and any(param in event_description for param in event_types):
            event_id = event_currency[1] + '_' + event_time_str

            event_intensity = {"1": 0, "2": 0, "3": 0, "priority": 0}

            for intence in intensity:
                _true = intence.find_all(class_="grayFullBullishIcon")
                _false = intence.find_all(class_="grayEmptyBullishIcon")

                if len(_true) == 1:
                    event_intensity['1'] += 1
                    event_intensity['priority'] = 1

                elif len(_true) == 2:
                    event_intensity['2'] += 1
                    event_intensity['priority'] = 2

                elif len(_true) == 3:
                    event_intensity['3'] += 1
                    event_intensity['priority'] = 3

            actual_value_tag = bl.find('td', id=lambda x: x and x.startswith('eventActual'))
            forecast_value_tag = bl.find(class_="fore")
            previous_value_tag = bl.find(class_="prev")

            actual_value = actual_value_tag.text.strip() if actual_value_tag else "Нет данных"
            forecast_value = forecast_value_tag.text.strip() if forecast_value_tag else "Нет данных"
            previous_value = previous_value_tag.text.strip() if previous_value_tag else "Нет данных"

            event_data = {
                'currency': event_currency[1],
                'event': event_description,
                'time': event_time,
                'intensity': event_intensity,
                'country': event_country,
                'actual_value': actual_value,
                'forecast_value': forecast_value,
                'previous_value': previous_value
            }

            result.append(event_data)

            # asyncio.create_task(schedule_notification(chat_id, event_time, event_description))


    driver.quit()
    return result


def scroll_down(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_week_events(event_types, countries, chat_id):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = "C:/Users/hogan/Downloads/chrome-win64/chrome-win64/chrome.exe"
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.investing.com/economic-calendar/")

    this_week_tab = driver.find_element(By.ID, "timeFrame_thisWeek")
    this_week_tab.click()

    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "economicCurrentTime")))
    button.click()

    moscow_timezone = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "liTz18")))
    moscow_timezone.click()
    time.sleep(2)

    scroll_down(driver)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    tables = soup.find_all("tr")

    result = []

    current_date = None

    for tr in tables:
        event_time_str = tr.find(class_="first left time js-time").text
        event_time = parse_event_time(event_time_str)

        date_element = tr.find("td", class_="theDay")
        if date_element:
            current_date = date_element.text.strip()
            continue

        event_time = tr.find(class_="first left time js-time")
        if event_time:
            event_time = event_time.text.strip()

            event_currency = tr.find(class_="left flagCur noWrap").text.split(' ')
            intensity = tr.find_all(class_="left textNum sentiment noWrap")
            event_country = tr.find(class_="left flagCur noWrap").find('span')['title']

            event_description = ""
            event_element = tr.find(class_='left event').a
            if event_element:
                event_description = event_element.text.strip()

            if event_country in countries and any(param in event_description for param in event_types):
                event_id = event_currency[1] + '_' + event_time_str

                event_intensity = {"1": 0, "2": 0, "3": 0, "priority": 0}

                for intence in intensity:
                    _true = intence.find_all(class_="grayFullBullishIcon")
                    _false = intence.find_all(class_="grayEmptyBullishIcon")

                    if len(_true) == 1:
                        event_intensity['1'] += 1
                        event_intensity['priority'] = 1
                    elif len(_true) == 2:
                        event_intensity['2'] += 1
                        event_intensity['priority'] = 2
                    elif len(_true) == 3:
                        event_intensity['3'] += 1
                        event_intensity['priority'] = 3

                actual_value_tag = tr.find('td', id=lambda x: x and x.startswith('eventActual'))
                forecast_value_tag = tr.find(class_="fore")
                previous_value_tag = tr.find(class_="prev")

                actual_value = actual_value_tag.text.strip() if actual_value_tag else "Нет данных"
                forecast_value = forecast_value_tag.text.strip() if forecast_value_tag else "Нет данных"
                previous_value = previous_value_tag.text.strip() if previous_value_tag else "Нет данных"

                event_data = {
                    'date': current_date,
                    'currency': event_currency[1],
                    'event': event_description,
                    'time': event_time,
                    'country': event_country,
                    'actual_value': actual_value,
                    'forecast_value': forecast_value,
                    'previous_value': previous_value
                }

                result.append(event_data)

                # asyncio.create_task(schedule_notification(chat_id, event_time, event_description))

    driver.quit()
    return result


