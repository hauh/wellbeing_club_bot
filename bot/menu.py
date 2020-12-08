"""Main conversation."""

import logging

from telegram.error import TelegramError
from telegram.ext import (
	CallbackQueryHandler, CommandHandler, Filters, MessageHandler
)

from bot.admin import admin_menu
from bot.replies import answers, cancel_sub, greetings, info_reply, offer_sub


def main_menu(update, context):
	subscribed = context.user_data.setdefault(
		'subscription_status',
		context.bot_data['db'].check_subscription(update.effective_user.id)
	)
	context.bot.reply(update, **(offer_sub if not subscribed else cancel_sub))


def start(update, context):
	update.effective_chat.send_message(greetings, queued=False)
	main_menu(update, context)


def subscribe(update, context):
	user = update.effective_user
	context.bot_data['db'].subscribe(user.id, user.username)
	context.user_data['subscription_status'] = True
	context.bot.reply(update, **cancel_sub, answer=answers['subscribed'])


def cancel_subscription(update, context):
	context.bot_data['db'].cancel_subscription(update.effective_user.id)
	context.user_data['subscription_status'] = False
	context.bot.reply(update, **offer_sub, answer=answers['cancelled'])


def info(update, context):
	context.bot.reply(update, **info_reply)


def clean(update, _context):
	update.effective_message.delete()


def subscribe_group(update, context):
	chat = update.effective_chat
	subscribed_chats = context.bot_data.setdefault('subscribed_chats', set())
	if chat not in subscribed_chats:
		subscribed_chats.add(chat)
		context.bot_data['db'].subscribe(chat.id, chat.title)


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
		main_menu(update, context)


def register_conversation(dispatcher):
	for handler in (
		CommandHandler('start', start, Filters.chat_type.private),
		MessageHandler(~Filters.chat_type.private, subscribe_group),
		CallbackQueryHandler(subscribe, pattern=r'^sub$'),
		CallbackQueryHandler(cancel_subscription, pattern=r'^cancel$'),
		CallbackQueryHandler(info, pattern=r'^info$'),
		CallbackQueryHandler(main_menu, pattern=r'^back$'),
		admin_menu,
		MessageHandler(Filters.chat_type.private, clean)
	):
		dispatcher.add_handler(handler)

	dispatcher.add_error_handler(error)
