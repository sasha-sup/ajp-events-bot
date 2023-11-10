from datetime import datetime

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

async def close_db_connection(connection):
    await connection.close()

async def create_tables_if_exists():
    connection = await create_db_connection()
    try:
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255));
            """)
    except asyncpg.PostgresError as e:
        logger.error(f"Error creating table: {e}")
    finally:
        await connection.close()

async def ensure_user_exists(user_id, username):
    connection = await create_db_connection()
    try:
        select_query = "SELECT user_id FROM users WHERE user_id = $1"
        user = await connection.fetchrow(select_query, user_id)
        if user is None:
            insert_query = "INSERT INTO users (user_id, username) VALUES ($1, $2)"
            await connection.execute(insert_query, user_id, username)
            logger.info(f"Added new user with user_id {user_id}, username {username}")
    except asyncpg.UniqueViolationError:
        logger.warning(f"User with user_id {user_id}, username {username} already exists.")
    except asyncpg.PostgresError as e:
        logger.error(f"Error adding user_id {user_id}, username {username}: {e}")
    finally:
        await connection.close()

async def get_all_user_ids():
    try:
        connection = await create_db_connection()
        query = "SELECT user_id FROM users"
        result = await connection.fetch(query)
        user_ids = [record['user_id'] for record in result]
        return user_ids
    except asyncpg.PostgresError as e:
        logger.error(f"Error get all user: {e}")
    finally:
        await connection.close()

async def get_user(user_id):
    try:
        connection = await create_db_connection()
        query = "SELECT user_id FROM users WHERE user_id = $1"
        result = await connection.fetchrow(query, user_id)
        return result
    except asyncpg.PostgresError as e:
        logger.error(f"Error get user_id {user_id}: {e}")
    finally:
        await connection.close()


async def update_notification_settings(user_id, send_notifications):
    connection = await create_db_connection()
    try:
        query = "UPDATE users SET send_notifications = $2 WHERE user_id = $1"
        await connection.execute(query, user_id, send_notifications)
    except asyncpg.PostgresError as e:
        logger.error(f"Error updating notification settings: {e}")
    finally:
        await connection.close()

async def fetch_events(year, selected_month):
    connection = await create_db_connection()
    try:
        query = """
            SELECT event_name, event_link, event_info, date, place
            FROM events
            WHERE year = $1 AND month = $2;
        """
        events = await connection.fetch(query, year, selected_month)
        return events
    except asyncpg.PostgresError as e:
        logger.error(f"Error in fetch_events: {e}")
        return []
    finally:
        await connection.close()

async def get_available_years():
    connection = await create_db_connection()
    try:
        query = "SELECT DISTINCT year FROM events"
        result = await connection.fetch(query)
        years = [row['year'] for row in result]
        return years
    except asyncpg.PostgresError as e:
        print(f"Error fetching available years: {e}")
    finally:
        await connection.close()

async def get_new_events():
    connection = await create_db_connection()
    current_date = datetime.now().strftime('%Y-%m-%d')
    try:
        query = """
            SELECT event_name, event_link, event_info, date, place
            FROM events
            WHERE added > $1
        """
        result = await connection.fetch(query, current_date)
        return result
    except asyncpg.PostgresError as e:
        print(f"Error in get_event_id: {e}")
    finally:
        await connection.close()


async def get_detailed_event():
    connection = await create_db_connection()
    try: 
        current_date = datetime.now().strftime('%Y-%m-%d')
        query = """
            SELECT event_title, event_info, event_details, image_url, schedule_data, register_url, event_link
            FROM detailed_events
            WHERE added > $1
        """
        events = await connection.fetch(query)
        return events
    except asyncpg.PostgresError as e:
        logger.error(f"Error in fetch_events: {e}")
        return []
    finally:
        await connection.close()