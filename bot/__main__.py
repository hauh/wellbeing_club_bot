"""Wellbeing Club Bot."""

import json
import logging
import sys

from telegram import ParseMode
from telegram.error import TelegramError
from telegram.ext import Defaults, Updater

from bot import POSTS_FILE, TOKEN
from bot.admin import admin_menu
from bot.channels import ChannelsCollection, ChannelsRegistrator
from bot.jobs import schedule_posts


def error(update, context):
	if not update or not update.effective_user:
		logging.error("Bot error - %s", context.error)
	else:
		try:
			update.effective_message.delete()
		except (AttributeError, TelegramError):
			pass
		user = update.effective_user.username or update.effective_user.id
		logging.warning("User '%s' error - %s", user, context.error)


def main():
	try:
		updater = Updater(TOKEN, defaults=Defaults(parse_mode=ParseMode.MARKDOWN))
	except TelegramError as err:
		logging.critical("Telegram connection error: %s", err)
		sys.exit(1)

	dispatcher = updater.dispatcher
	dispatcher.bot_data['channels'] = ChannelsCollection()
	dispatcher.add_handler(ChannelsRegistrator())
	dispatcher.add_handler(admin_menu)
	dispatcher.add_error_handler(error)

	updater.start_polling()

	try:
		with open(POSTS_FILE) as f:
			posts = json.load(f)
			schedule_posts(dispatcher.job_queue, posts)
	except (FileNotFoundError, json.JSONDecodeError):
		pass

	logging.info("Bot started!")
	updater.idle()
	logging.info("Turned off.")


if __name__ == "__main__":
	main()
