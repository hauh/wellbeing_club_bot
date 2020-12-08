"""Wellbeing Club Bot."""

import logging
import os
import sys
from sqlite3 import DatabaseError

from telegram.constants import MESSAGEENTITY_MENTION
from telegram.error import TelegramError
from telegram.ext import (
	CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater
)

from bot import menu
from bot.admin import admin_menu
from bot.botclass import WellbeingClubBot
from bot.database import Database
from bot.jobs import schedule_posts


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
		admin = int(os.environ['ADMIN'])
	except KeyError:
		logging.critical("ADMIN environment variable required.")
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
	dispatcher.bot_data['admin'] = admin
	dispatcher.bot_data['db'] = database

	dispatcher.add_handler(CommandHandler(
		'start', menu.start,
		Filters.chat_type.private
	))
	dispatcher.add_handler(CommandHandler(
		'start', menu.add_group,
		Filters.chat_type.groups & Filters.entity(MESSAGEENTITY_MENTION)
	))
	dispatcher.add_handler(CallbackQueryHandler(menu.back, pattern=r'^back$'))
	dispatcher.add_handler(CallbackQueryHandler(menu.subscribe, pattern=r'^sub$'))
	dispatcher.add_handler(CallbackQueryHandler(menu.cancel, pattern=r'^cancel$'))
	dispatcher.add_handler(CallbackQueryHandler(menu.info, pattern=r'^info$'))
	dispatcher.add_handler(admin_menu)
	dispatcher.add_handler(MessageHandler(Filters.chat_type.private, menu.clean))

	dispatcher.add_error_handler(menu.error)

	updater.start_polling()
	schedule_posts(updater.bot, dispatcher.job_queue, database.get_posts())
	logging.info("Bot started!")

	updater.idle()
	logging.info("Turned off.")


if __name__ == "__main__":
	main()
