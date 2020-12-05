"""Main conversation."""

import logging

from telegram.error import TelegramError

from bot import replies
from bot.replies import reply


def start(update, context):
	subscribed = context.user_data.setdefault(
		'subscription_status',
		context.bot_data['db'].check_subscription(update.effective_user.id)
	)
	reply(update, **(replies.offer_sub if not subscribed else replies.cancel_sub))


def add_group(update, context):
	chat = update.effective_chat
	if not context.bot_data['db'].check_subscription(chat.id):
		context.bot_data['db'].subscribe(chat.id, chat.title)
		update.effective_message.reply_text(replies.group_subscribed)


def subscribe(update, context):
	user = update.effective_user
	context.bot_data['db'].subscribe(user.id, user.username)
	context.user_data['subscription_status'] = True
	reply(update, **replies.cancel_sub, answer='subscribed')


def cancel(update, context):
	context.bot_data['db'].cancel_subscription(update.effective_user.id)
	context.user_data['subscription_status'] = False
	reply(update, **replies.offer_sub, answer='cancelled')


def info(update, _context):
	reply(update, **replies.info)


def clean(update, _context):
	update.effective_message.delete()


def back(update, context):
	start(update, context)
	return -1


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
