"""Bot replies."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


sub_button = [InlineKeyboardButton("Подписаться", callback_data='sub')]
cancel_button = [InlineKeyboardButton("Отключить", callback_data='cancel')]
info_button = [InlineKeyboardButton("Информация", callback_data='info')]
back_button = [InlineKeyboardButton("Назад", callback_data='back')]

offer_sub = {
	'text': "Привет!\nХотите подписаться на хорошие новости?",
	'reply_markup': InlineKeyboardMarkup([sub_button, info_button])
}
cancel_sub = {
	'text': "Вы подписаны. Отключить получение новостей?",
	'reply_markup': InlineKeyboardMarkup([cancel_button, info_button])
}
info = {
	'text': "Какая-то информация здесь",
	'reply_markup': InlineKeyboardMarkup([back_button])
}

answers = {
	'subscribed': "Вы подписаны!",
	'cancelled': "Вы отписаны :("
}
