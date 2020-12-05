"""Scheduled messages."""

import logging

from telegram.error import TelegramError


def send_message(context):
	text, image = context.job.context
	chats_sent = []
	for chat_id, *_ in context.bot_data['db'].get_chats():
		try:
			context.bot.send_message(chat_id, text + image)
		except TelegramError as err:
			if str(err) == "Chat not found":
				context.bot_data['db'].cancel_subscription(chat_id)
			else:
				logging.error("Scheduled message error - %s", err)
		else:
			chats_sent.append(str(chat_id))
	logging.info("Message sent to %s chats.", len(chats_sent))
	context.bot_data['db'].posted(context.job.name, chats_sent)


def schedule_posts(job_queue, posts):
	job_queue.scheduler.remove_all_jobs()
	for post in posts:
		job_queue.run_once(
			send_message,
			when=post[0],
			name=str(post[0]),
			context=(post[1], post[2])
		)
