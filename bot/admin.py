"""Admin menu."""

import json
import logging
from datetime import timezone

from telegram.constants import CHAT_PRIVATE
from telegram.error import TelegramError
from telegram.ext import (
	CallbackQueryHandler, ConversationHandler, Filters, MessageHandler
)
from telegram.ext.filters import MessageFilter
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from bot import ADMINS, POSTS_FILE
from bot.excel import ParseError, parse_document
from bot.jobs import schedule_posts

admin_reply = (
	"Меню управления.\n"
	"*Загрузите файл .xlsx* c расписанием публикаций.\n"
	"Формат документа: B - дата публикации, C - время, D - заголовок, "
	"E - текст, F - рекомендации, G - изображение.\n"
	"Публикации будут отправлены в этот чат для проверки."
)
parse_failed = "Ошибка загрузки публикаций из файла:\n{}"
empty_file = "Новые публикации не найдены в файле."
check_failed = "*Публикация {} не отправляется*. Ответ телеграма:\n```{}```"
confirm = "Подвердите новое расписание. Всего публикаций: {}."
success = "Расписание обновлено."

confirm_keyboard = InlineKeyboardMarkup([
	[InlineKeyboardButton("Обновить", callback_data=r'update')],
	[InlineKeyboardButton("Отмена", callback_data=r'cancel')]
])


class AdminFilter(MessageFilter):
	"""Filtering out non-private non-admin messages."""

	def filter(self, message):
		return message.chat.type == CHAT_PRIVATE and message.from_user.id in ADMINS


def reply(update, text, buttons=None, answer=None):
	"""Wrapper function for responses to user."""
	update.effective_chat.send_message(text, reply_markup=buttons)
	if update.callback_query:
		try:
			update.callback_query.answer(text=answer)
			update.callback_query.delete_message()
		except TelegramError as err:
			logging.warning("Cleaning chat error - %s", err)


def admin_main(update, _context):
	reply(update, admin_reply)
	return 1


def check_file(update, context):
	file = update.effective_message.document.get_file()
	try:
		posts = parse_document(file.download())
	except ParseError as err:
		reply(update, parse_failed.format(str(err)))
		return None

	if not posts:
		reply(update, empty_file)
		return None

	for post in posts:
		time, text, image = post
		check_text = f"{text}\n\n_{time.strftime('%d.%m.%Y %H:%M')}_"
		try:
			if image:
				message = update.effective_chat.send_photo(image, check_text)
				post[2] = message['photo'][-1]['file_id']
			else:
				update.effective_chat.send_message(check_text)
		except TelegramError as err:
			reply(update, check_failed.format(str(time), str(err)))
			return None
		else:
			post[0] = time.astimezone(timezone.utc).replace(tzinfo=None).isoformat()

	context.user_data['new_posts'] = posts
	reply(update, confirm.format(len(posts)), confirm_keyboard)
	return 2


def update_schedule(update, context):
	posts = context.user_data.pop('new_posts')
	with open(POSTS_FILE, 'w') as f:
		json.dump(posts, f)
	schedule_posts(context.job_queue, posts)
	update.callback_query.answer(success)
	return admin_main(update, context)


admin_menu = ConversationHandler(
	entry_points=[MessageHandler(AdminFilter() & Filters.text, admin_main)],
	states={
		1: [MessageHandler(
			AdminFilter() & Filters.document.file_extension("xlsx"),
			check_file
		)],
		2: [CallbackQueryHandler(update_schedule, pattern=r'^update$')]
	},
	fallbacks=[CallbackQueryHandler(admin_main, pattern=r'^cancel$')],
	allow_reentry=True
)
