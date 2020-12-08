"""Scheduled messaging."""

import logging
from datetime import datetime, timedelta
from functools import partial

from telegram.error import BadRequest, ChatMigrated, RetryAfter, Unauthorized


def messaging(context):
	job_name = context.job.name
	messager, chats, retries = context.job.context
	chats = chats or context.bot_data['db'].get_chats()
	logging.info("[%s] Messaging to %s chats started.", job_name, len(chats))

	sent, retry = [], []
	for promise in [messager(chat_id, isgroup=chat_id < 0) for chat_id in chats]:
		chat_id = promise.args[1]
		try:
			result = promise.result(timeout=3600)
		except Unauthorized:
			context.bot_data['db'].cancel_subscription(chat_id)
		except ChatMigrated as err:
			context.bot_data['db'].change_chat_id(chat_id, err.new_chat_id)
			retry.append(err.new_chat_id)
		except RetryAfter:
			retry.append(chat_id)
		except Exception as err:  # pylint: disable=broad-except
			if isinstance(err, BadRequest) and str(err) == "Chat not found":
				context.bot_data['db'].cancel_subscription(chat_id)
			else:
				logging.warning("[%s] Skipping chat '%s' - %s", job_name, chat_id, err)
		else:
			(sent if result else retry).append(chat_id)

	if retry:
		if retries < 3:
			logging.info("[%s] %s chats left. Retry in one hour.", job_name, len(retry))
			retry_time = datetime.now() + timedelta(hours=1)
			retry_context = (messager, retry, retries + 1)
			context.job_queue.run_once(messaging, retry_time, retry_context, job_name)
		else:
			logging.warning("[%s] After 3 retries %s chats left.", job_name, len(retry))

	if sent:
		logging.info("[%s] Messages sent: %s / %s.", job_name, len(sent), len(chats))
		context.bot_data['db'].posted(context.job.name, sent)


def schedule_posts(bot, job_queue, posts):
	job_queue.scheduler.remove_all_jobs()
	for post_time, text, tg_image_id in posts:
		if tg_image_id:
			messager = partial(bot.send_photo, photo=tg_image_id, caption=text)
		else:
			messager = partial(bot.send_message, text=text)
		job_queue.run_once(messaging, post_time, (messager, None, 0), str(post_time))
	logging.info("Scheduled %s posts.", len(posts))
