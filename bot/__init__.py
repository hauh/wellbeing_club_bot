"""Wellbeing Club Bot package."""

import logging
import os
import sys
from datetime import timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(funcName)s - %(message)s",
)

try:
	TOKEN = os.environ['TOKEN']
except KeyError:
	logging.critical("TOKEN environment variable required.")
	sys.exit(1)

try:
	ADMINS = set(int(admin_id) for admin_id in os.environ['ADMINS'].split(','))
except KeyError:
	logging.critical("ADMINS environment variable required.")
	sys.exit(1)
except ValueError:
	logging.critical("Admin ID must be a number.")
	sys.exit(1)

try:
	FILE_TIME = ZoneInfo('Europe/Moscow')
except ZoneInfoNotFoundError:
	logging.warning("Time zone info not found, using UTC+3.")
	FILE_TIME = timezone(timedelta(hours=3), 'Europe/Moscow')

POSTS_FILE = 'data/posts.json'
CHANNELS_FILE = 'data/channels.json'
