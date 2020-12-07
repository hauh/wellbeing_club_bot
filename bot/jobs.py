"""Scheduled messaging."""

import logging
from datetime import datetime, timedelta
from functools import partial

from telegram.error import BadRequest, ChatMigrated, RetryAfter, Unauthorized


def send_message(context):
	text, tg_image_id, chats = context.job.context
	if tg_image_id:
		send = partial(context.bot.send_photo, photo=tg_image_id, caption=text)
	else:
		send = partial(context.bot.send_message, text=text)

	sent_chats, retry_chats = [], []
	chats = chats or (chat[0] for chat in context.bot_data['db'].get_chats())
	for promise in [send(chat_id, isgroup=chat_id < 0) for chat_id in chats]:
		chat_id = promise.args[1]
		try:
			result = promise.result(timeout=3600)
		except Unauthorized:
			context.bot_data['db'].cancel_subscription(chat_id)
		except ChatMigrated as err:
			context.bot_data['db'].change_chat_id(chat_id, err.new_chat_id)
			retry_chats.append(err.new_chat_id)
		except RetryAfter as err:
			retry_chats.append(chat_id)
		except Exception as err:  # pylint: disable=broad-except
			if isinstance(err, BadRequest) and str(err) == "Chat not found":
				context.bot_data['db'].cancel_subscription(chat_id)
			else:
				logging.error("Chat %s message error - %s", chat_id, err)
		else:
			(sent_chats if result else retry_chats).append(chat_id)

	if not sent_chats:
		logging.error("No messages were sent.")
	else:
		if retry_chats:
			context.job_queue.run_once(
				send_message,
				datetime.now() + timedelta(hours=1),
				(text, tg_image_id, retry_chats),
				context.job.name + "_[retry]",
			)
			logging.info("Some chats left. Retry in one hour.")
		logging.info("Message sent to %s chats.", len(sent_chats))
		context.bot_data['db'].posted(context.job.name, sent_chats)


def schedule_posts(job_queue, posts):
	job_queue.scheduler.remove_all_jobs()
	for timestamp, text, tg_image_id in posts:
		context = (text, tg_image_id, None)
		job_queue.run_once(send_message, timestamp, context, str(timestamp))
