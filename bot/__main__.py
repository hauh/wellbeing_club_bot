"""Wellbeing Club Bot."""

import logging
import os
import sys
from sqlite3 import DatabaseError

from telegram.error import TelegramError
from telegram.ext import Updater

from bot.botclass import WellbeingClubBot
from bot.database import Database
from bot.jobs import schedule_posts
from bot.menu import register_conversation


def main():
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",
	)

	try:
		token = os.environ['TOKEN']
	except KeyError:
		logging.critical("TOKEN environment variable required.")
		sys.exit(1)

	try:
		admins = set(int(admin_id) for admin_id in os.environ['ADMINS'].split(','))
	except KeyError:
		logging.critical("ADMINS environment variable required.")
		sys.exit(1)
	except ValueError:
		logging.critical("Admin ID must be a number.")
		sys.exit(1)

	try:
		database = Database('data/wellbeing_club.db')
	except DatabaseError as err:
		logging.critical("Database error - %s", err)
		sys.exit(1)

	try:
		updater = Updater(bot=WellbeingClubBot(token))
	except TelegramError as err:
		logging.critical("Telegram connection error - %s", err)
		sys.exit(1)

	dispatcher = updater.dispatcher
	dispatcher.bot_data['admins'] = admins
	dispatcher.bot_data['db'] = database
	register_conversation(dispatcher)

	updater.start_polling()
	schedule_posts(updater.bot, dispatcher.job_queue, database.get_posts())
	logging.info("Bot started!")

	updater.idle()
	logging.info("Turned off.")


if __name__ == "__main__":
	main()
