"""Main conversation."""

import logging

from telegram.error import BadRequest, TelegramError
from bot import responses


def reply(update, response):
	update.effective_chat.send_message(**response)
	if update.callback_query:
		try:
			update.callback_query.answer()
			update.callback_query.delete_message()
		except BadRequest as err:
			logging.warning("Cleaning chat error - %s", err)


def start(update, context):
	subscribed = context.user_data.setdefault(
		'subscription_status',
		context.bot_data['db'].check_subscription(update.effective_user.id)
	)
	reply(update, responses.offer_sub if not subscribed else responses.cancel_sub)


def subscribe(update, context):
	user = update.effective_user
	context.bot_data['db'].subscribe(user.id, user.username)
	update.callback_query.answer(responses.answers['subscribed'])
	reply(update, responses.cancel_sub)


def cancel(update, context):
	context.bot_data['db'].cancel_subscription(update.effective_user.id)
	update.callback_query.answer(responses.answers['cancelled'])
	reply(update, responses.offer_sub)


def info(update, _context):
	reply(update, responses.info)


def clean(update, _context):
	update.effective_message.delete()


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
		start(update, context)
