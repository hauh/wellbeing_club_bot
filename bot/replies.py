"""Bot replies."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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
info_reply = {
	'text': "Какая-то информация здесь",
	'buttons': InlineKeyboardMarkup([back_btn])
}
group_added = "Группа подписана."

# admin #
upload_btn = [InlineKeyboardButton("Загрузить файл", callback_data='upload')]
stats_btn = [InlineKeyboardButton("Статистика", callback_data='stats')]
update_btn = [InlineKeyboardButton("Обновить", callback_data='update')]

admin = {
	'text': "Меню управления.\nОбновите расписание или скачайте статистку.",
	'buttons': InlineKeyboardMarkup([upload_btn, stats_btn, back_btn])
}
stats = {
	'text': "Здесь будет статистика.",
	'buttons': InlineKeyboardMarkup([back_btn])
}
upload = {
	'text': (
		"Загрузите файл .xlsx c расписанием публикаций.\n"
		"Формат документа: B - дата публикации, C - время, D - заголовок, "
		"E - текст, F - рекомендации, G - изображение.\n"
		"Публикации будут отправлены в этот чат для проверки."
	),
	'buttons': InlineKeyboardMarkup([back_btn])
}
update = {
	'parse_failed': {
		'text': "Ошибка загрузки публикаций из файла:\n{}",
		'buttons': InlineKeyboardMarkup([back_btn])
	},
	'empty': {
		'text': "Новые публикации не найдены в файле.",
		'buttons': InlineKeyboardMarkup([back_btn])
	},
	'check_failed': {
		'text': "*Публикация {} не отправляется*. Ответ телеграма:\n```{}```",
		'buttons': InlineKeyboardMarkup([back_btn])
	},
	'success': {
		'text': "Подвердите новое расписание. Всего публикаций: {}.",
		'buttons': InlineKeyboardMarkup([update_btn, back_btn])
	}
}

# callback query answers #
answers = {
	'subscribed': "Вы подписаны!",
	'cancelled': "Вы отписаны :(",
	'updated': "Расписание обновлено."
}
