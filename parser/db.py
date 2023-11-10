import asyncio
import os
from datetime import datetime
import json
import asyncpg
import config
from config import logger


async def create_db_connection():
    db_config = {
        "host": config.DB_HOST,
        "port": config.DB_PORT,
        "database": config.DB_NAME,
        "user": config.DB_USER,
        "password": config.DB_PASS,
    }
    try:
        # Connect db
        connection = await asyncpg.connect(**db_config)
        return connection
    except asyncpg.PostgresError as e:
        logger.error(f"Error connecting to DB: {e}")
        raise e

async def create_tables_if_exist():
    connection = await create_db_connection()
    try:
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                added DATE,
                year INT NOT NULL,
                month VARCHAR(20) NOT NULL,
                event_name TEXT NOT NULL,
                event_link TEXT NOT NULL,
                event_info TEXT NOT NULL,
                date TEXT NOT NULL,
                place TEXT NOT NULL);
        """)
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS detailed_events (
                id SERIAL PRIMARY KEY,
                added DATE,
                event_title TEXT NOT NULL,
                event_info TEXT NOT NULL,
                event_details TEXT NOT NULL,
                image_url TEXT NULL,
                schedule_data TEXT NOT NULL,
                register_url TEXT NOT NULL);
        """)
    except asyncpg.PostgresError as e:
        logger.error(f"Error creating tables: {e}")
    finally:
        await connection.close()

async def store_events_in_db(year, month, event_name, event_link, event_info, date, place):
    connection = await create_db_connection()
    try:
        query = """
            INSERT INTO events (added, year, month, event_name, event_link, event_info, date, place) 
            VALUES (CURRENT_DATE, $1, $2, $3, $4, $5, $6, $7)
        """
        await connection.execute(query, year, month, event_name, event_link, event_info, date, place)
        logger.info(f"Added new event: {event_name}")
    except asyncpg.PostgresError as e:
        logger.error(f"Error in store_events_in_db: {e}")
    finally:
        await connection.close()

async def store_detailed_event_in_db(event_title, event_info, event_details, image_url, schedule_data, register_url, event_link):
    connection = await create_db_connection()
    try:
        event_details_json = json.dumps(event_details)
        schedule_data_json = json.dumps(schedule_data)
        query = """
            INSERT INTO detailed_events (added, event_title, event_info, event_details, image_url, schedule_data, register_url, event_link)
            VALUES (CURRENT_DATE, $1, $2, $3, $4, $5, $6, $7)
        """
        await connection.execute(query, event_title, event_info, event_details_json, image_url, schedule_data_json, register_url, event_link)
        logger.info(f"Added new detailed event: {event_title}")
    except asyncpg.PostgresError as e:
        logger.error(f"Error in store_detailed_event_in_db: {e}")
    finally:
        await connection.close()

async def check_event_in_db(event_link):
    connection = await create_db_connection()
    try:
        query = "SELECT event_link FROM events WHERE event_link = $1"
        result = await connection.fetch(query, event_link)
        return result
    except asyncpg.PostgresError as e:
        logger.error(f"Error in check_event_in_db: {e}")
        return None
    finally:
        await connection.close()

async def check_event_in_detailed_db(event_link):
    connection = await create_db_connection()
    try:
        query = "SELECT event_link FROM detailed_events WHERE event_link = $1"
        result = await connection.fetch(query, event_link)
        return result
    except asyncpg.PostgresError as e:
        logger.error(f"Error in check_event_in_detailed_db: {e}")
        return None
    finally:
        await connection.close()

async def get_event_url():
    connection = await create_db_connection()
    try:
        query = "SELECT event_link FROM events WHERE year = 2024"
        result = await connection.fetch(query)
        urls = [record['event_link'] for record in result]
        return urls
    except asyncpg.PostgresError as e:
        logger.error(f"Error in get_event_url: {e}")
    finally:
        await connection.close()
