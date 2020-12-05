"""Bot replies."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest

back_btn = [InlineKeyboardButton("Назад", callback_data='back')]

# main #
sub_btn = [InlineKeyboardButton("Подписаться", callback_data='sub')]
cancel_btn = [InlineKeyboardButton("Отключить", callback_data='cancel')]
info_btn = [InlineKeyboardButton("Информация", callback_data='info')]

offer_sub = {
	'text': "Привет!\nХотите подписаться на хорошие новости?",
	'buttons': InlineKeyboardMarkup([sub_btn, info_btn])
}
cancel_sub = {
	'text': "Вы подписаны. Отключить получение новостей?",
	'buttons': InlineKeyboardMarkup([cancel_btn, info_btn])
}
info = {
	'text': "Какая-то информация здесь",
	'buttons': InlineKeyboardMarkup([back_btn])
}

# admin #
upload_btn = [InlineKeyboardButton("Загрузить файл", callback_data='upload')]
stats_btn = [InlineKeyboardButton("Статистика", callback_data='stats')]
update_btn = [InlineKeyboardButton("Обновить", callback_data='update')]

admin = {
	'text': "Меню управления.\nОбновите посты или скачайте статистку.",
	'buttons': InlineKeyboardMarkup([upload_btn, stats_btn, back_btn])
}
stats = {
	'text': "Здесь будет статистика.",
	'buttons': InlineKeyboardMarkup([back_btn])
}
upload = {
	'text': (
		"Загрузите файл .xlsx с постами. "
		"Новые по времени сообщения будут отправлены в этот чат для проверки."
	),
	'buttons': InlineKeyboardMarkup([back_btn])
}
update_result = {
	'fail': {
		'text': "Ошибка в файле:\n{}\nИсправьте и попробуйте ещё раз.",
		'buttons': InlineKeyboardMarkup([back_btn])
	},
	'empty': {
		'text': "Новые сообщения не обнаружены. Попробуйте другой файл.",
		'buttons': InlineKeyboardMarkup([back_btn])
	},
	'success': {
		'text': "Новых сообщений: {}",
		'buttons': InlineKeyboardMarkup([update_btn, back_btn])
	}
}

# callback query answers #
answers = {
	'subscribed': "Вы подписаны!",
	'cancelled': "Вы отписаны :(",
	'updated': "Расписание обновлено."
}


def reply(update, text, buttons, answer=None):
	update.effective_chat.send_message(text, reply_markup=buttons)
	if update.callback_query:
		try:
			update.callback_query.answer(text=answers.get(answer))
			update.callback_query.delete_message()
		except BadRequest as err:
			logging.warning("Cleaning chat error - %s", err)
