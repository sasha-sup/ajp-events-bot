import asyncio
import os
import parser

import config
import db
from config import logger

dirs_created = False

def create_content_dirs():
    try:
        dir_path = "/app/log"
        if not os.path.exists(dir_path):
            logger.info(f"Created directory: {dir_path}")
            os.makedirs(dir_path)
        else:
            logger.info(f"Directory already exists: {dir_path}")
        dirs_created = True
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
        raise e

async def main():
    create_content_dirs()
    await db.create_tables_if_exist()
    await parser.fetch_and_parse_events()
    await parser.deep_parse()

if __name__ == '__main__':
    asyncio.run(main())
