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


def admin(update, context):
	if update.effective_user.id != context.bot_data['admin']:
		update.effective_message.delete()
		return -1
	context.bot.reply(update, **replies.admin)
	return 1


def stats(update, context):
	context.bot.reply(update, **replies.stats)
	return -1


def upload_file(update, context):
	context.bot.reply(update, **replies.upload)
	return 2


def new_posts(update, context):
	file = update.effective_message.document.get_file()
	try:
		posts = parse_document(file.download())
	except ParseError as err:
		reply = replies.update['parse_failed']
		context.bot.reply(update, reply['text'].format(str(err)), reply['buttons'])
		return 2

	if not posts:
		context.bot.reply(update, **replies.update['empty'])
		return 2

	for post in posts:
		text = f"{post[1]}\n\n_{post[0]}_"
		try:
			if post[2]:
				message = update.effective_chat.send_photo(post[2], text, queued=False)
				post[2] = message['photo'][-1]['file_id']
			else:
				update.effective_chat.send_message(text, queued=False)
		except TelegramError as err:
			reply = replies.update['check_failed']
			reply_text = reply['text'].format(str(post[0]), str(err))
			context.bot.reply(update, reply_text, reply['buttons'])
			return 2

	context.user_data['new_posts'] = posts
	reply = replies.update['success']
	context.bot.reply(update, reply['text'].format(len(posts)), reply['buttons'])
	return 3


def update_schedule(update, context):
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
			CallbackQueryHandler(upload_file, pattern=r'^upload$')
		],
		2: [MessageHandler(
			Filters.chat_type.private & Filters.document.file_extension("xlsx"),
			new_posts
		)],
		3: [CallbackQueryHandler(update_schedule, pattern=r'^update$')]
	},
	fallbacks=[CallbackQueryHandler(back, pattern=r'^back$')],
	allow_reentry=True
)
