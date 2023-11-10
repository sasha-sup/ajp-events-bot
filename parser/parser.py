import asyncio
import json
import os
import re
from datetime import datetime

import aiohttp
import config
import db
from bs4 import BeautifulSoup
from config import logger

month_names = {
    "JANUARY": 1,
    "FEBRUARY": 2,
    "MARCH": 3,
    "APRIL": 4,
    "MAY": 5,
    "JUNE": 6,
    "JULY": 7,
    "AUGUST": 8,
    "SEPTEMBER": 9,
    "OCTOBER": 10,
    "NOVEMBER": 11,
    "DECEMBER": 12
}

async def fetch_and_parse_events():
    try:
        logger.info("Fetching events from the website.")
        async with aiohttp.ClientSession() as session:
            async with session.get(config.URL) as response:
                response.raise_for_status()
                content = await response.text()
        soup = BeautifulSoup(content, 'html.parser')
        events = []
        year = None
        page_container = soup.find("div", class_="page-container page-view content")
        if page_container:
            for element in page_container.find_all(["h1", "h2", "p"]):
                if element.name == "h1":
                    year_text = element.text.strip()
                    if not re.match(r'^\d{4}$', year_text):
                        continue
                    year = int(year_text)
                    logger.info(f"Found year: {year}")
                elif element.name == "h2" and year is not None:
                    month_name = element.text.strip()
                    month_number = int(month_names.get(month_name))
                    if month_number:
                        logger.info(f"Found month: {month_name} ({month_number})")
                    else:
                        logger.error(f"Unknown month name: {month_name}")
                elif element.name == "p":
                    event_url = element.find("a")
                    if event_url:
                        event_name = event_url.text.strip()
                        event_link = event_url["href"]
                        event_info = element.text.strip().replace(event_name, "").strip()
                        date_pattern = r'\d{4}\s+\w+(?:\s+\d{1,2}(?:\s*-\s*\d{1,2})?)?'
                        place_pattern = r'@ (.+)'
                        date_match = re.search(date_pattern, event_info)
                        place_match = re.search(place_pattern, event_info)
                        if date_match and place_match:
                            date = date_match.group()
                            place = place_match.group(1)
                        else:
                            date = ""
                            place = ""
                        existing_event = await db.check_event_in_db(event_link)
                        if not existing_event:
                            await db.store_events_in_db(year, month_number, event_name, event_link, event_info, date, place)
        logger.info("Finished fetching and parsing events.")
    except Exception as e:
        logger.error(f"Error in fetch_and_parse_events: {e}")

async def deep_parse():
    parsed_data = []
    try:
        all_urls = await db.get_event_url()
        for url in all_urls:
            event_link = url
            try:
                logger.info(f"Fetching events from the website: {event_link}")
                async with aiohttp.ClientSession() as session:
                    async with session.get(event_link) as response:
                        response.raise_for_status()
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
            except aiohttp.ClientError as ce:
                logger.error(f"AIOHTTP ClientError: {ce}")
            except aiohttp.ServerTimeoutError as ste:
                logger.error(f"AIOHTTP ServerTimeoutError: {ste}")
            except aiohttp.ClientResponseError as cre:
                logger.error(f"AIOHTTP ClientResponseError: {cre}")
            except aiohttp.ClientConnectionError as cce:
                logger.error(f"AIOHTTP ClientConnectionError: {cce}")
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
# Title
            try:
                event_title = soup.find('h1').text.strip()
                logger.info(f"Found {event_title}")
            except AttributeError:
                logger.error("Event title not found")
# Event info
            try:
                info_element = soup.find('div', class_='information margin-bottom-xs-64')
                event_info = info_element.find('h2').text.strip() if info_element and info_element.find('h2') else ''
                logger.info("Found event info")
            except AttributeError:
                logger.error("Event info not found")
# Event details
            try:
                h2_element = soup.find('h2', text=re.compile(r'BELT AND AGE DIVISIONS'))
                exclude_pattern = re.compile(r'(For all information|AJP Competition|_{1,100}|To Be Confirmed Soon)')
                exclude_next_p = False
                p_texts = []
                for p in h2_element.find_all_next('p'):
                    p_text = p.get_text(strip=True)
                    if exclude_pattern.search(p_text):
                        exclude_next_p = not exclude_next_p
                    elif not exclude_next_p and not p_text.startswith("Year of Birth"):
                        p_texts.append(p_text)
                event_details = {}
                current_group = None

                for item in p_texts:
                    if item:
                        if item.endswith(":"):
                            current_group = item
                            event_details[current_group] = []
                        else:
                            event_details[current_group].append(item)
                logger.info("Found Event details")
            except AttributeError:
                logger.error("Event details not found")
# Event image
            try:
                cover_image = soup.find('div', class_='cover-image')
                image_url = cover_image.find('img')['src'] if cover_image and cover_image.find('img') else ''
                if "/build/webpack/img/ajp/fallback.a01f59147724b9274315365bd75f5b21.jpg" in image_url:
                    image_url = None
                logger.info("Found Event image")
            except AttributeError:
                logger.error("Event image not found")
# Schedule items
            try:
                schedule_items = soup.find_all('div', class_='schedule-item')
                schedule_data = []
                for schedule_item in schedule_items:
                    title_element = schedule_item.find(class_="title")
                    strong_element = schedule_item.find("strong")
                    small_element = schedule_item.find("small")
                    if title_element is not None and strong_element is not None and small_element is not None:
                        title = clean_text(title_element.get_text(strip=True))
                        strong_text = clean_text(strong_element.get_text(strip=True))
                        small_text = clean_text(small_element.get_text(strip=True))
                        schedule_data.append({'title': title,'date': strong_text, 'time': small_text})
                logger.info("Found Schedule items")
            except Exception as e:
                logger.error(f"Event Schedule not found: {e}")
# Register button
            try:
                register_url = soup.find('a', class_='register')['href'] if soup.find('a', class_='register') else ''
                logger.info("Found Register url")
            except AttributeError:
                logger.error("Register url not found")
# Result
            parsed_data = []
            for item in parsed_data:
                item_data = {
                    'event_title': clean_text(item['event_title']),
                    'event_info': clean_text(item['event_info']),
                    'event_details': [clean_text(event_details) for detail in item['event_details']],
                    'image_url': clean_text(item['image_url']),
                    'schedule_data': schedule_data,
                    'register_url': clean_text(item['register_url'])
                }
                parsed_data.append(item_data)
            existing_event = await db.check_event_in_detailed_db(event_link)
            if not existing_event:
                 await db.store_detailed_event_in_db(event_title, event_info, event_details, image_url, schedule_data, register_url, event_link)
    except Exception as e:
        logger.error(f"Error during deep parsing: {e}")
        return []

def clean_text(text):
    cleaned_text = re.sub(r'\s+', ' ', text).replace('\xa0', '')
    return cleaned_text