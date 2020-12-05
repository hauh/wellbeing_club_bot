"""Admin menu."""

from telegram.error import TelegramError
from telegram.ext import (
	CallbackQueryHandler, CommandHandler, ConversationHandler, Filters,
	MessageHandler
)

from bot import replies
from bot.excel import ParseError, parse_document
from bot.jobs import schedule_posts
from bot.menu import back
from bot.replies import reply


def admin(update, context):
	if update.effective_user.id != context.bot_data['admin']:
		update.effective_message.delete()
		return -1
	reply(update, **replies.admin)
	return 1


def stats(update, _context):
	reply(update, **replies.stats)
	return -1


def update_posts(update, _context):
	reply(update, **replies.upload)
	return 2


def get_posts(update, context):
	file = update.effective_message.document.get_file()
	try:
		posts = parse_document(file.download())
	except ParseError as err:
		response = replies.update_result['fail']
		reply(update, response['text'].format(str(err)), response['buttons'])
		return 2

	if not posts:
		reply(update, **replies.update_result['empty'])
		return 2

	try:
		for post in posts:
			text = f"{str(post[0])}:\n{post[1]}\n{post[2]}"
			update.effective_chat.send_message(text)
	except TelegramError as err:
		response = replies.update_result['fail']
		reply(update, response['text'].format(str(err)), response['buttons'])
		return 2

	context.user_data['new_posts'] = posts
	response = replies.update_result['success']
	reply(update, response['text'].format(len(posts)), response['buttons'])
	return 3


def new_schedule(update, context):
	posts = context.user_data.pop('new_posts')
	context.bot_data['db'].save_posts(posts)
	schedule_posts(context.job_queue, posts)
	update.callback_query.answer(replies.answers['updated'])
	return back(update, context)


admin_menu = ConversationHandler(
	entry_points=[CommandHandler('admin', admin, Filters.chat_type.private)],
	states={
		1: [
			CallbackQueryHandler(stats, pattern=r'^stats$'),
			CallbackQueryHandler(update_posts, pattern=r'^upload$')
		],
		2: [MessageHandler(
			Filters.chat_type.private & Filters.document.file_extension("xlsx"),
			get_posts
		)],
		3: [CallbackQueryHandler(new_schedule, pattern=r'^update$')]
	},
	fallbacks=[CallbackQueryHandler(back, pattern=r'^back$')],
	allow_reentry=True
)
