"""Scheduled messaging."""

import logging
from datetime import datetime
from functools import partial
from time import sleep

from telegram.error import BadRequest, ChatMigrated, Unauthorized


def post_to_channels(context, channels=None, retries=0):
	text, tg_image_id = context.job.context
	channels = channels or context.bot_data['channels']
	logging.info(
		"Posting <%s> to %s%s.",
		context.job.name, channels,
		f" (retry {retries})" if retries else ""
	)

	if tg_image_id:
		posting = partial(context.bot.send_photo, photo=tg_image_id, caption=text)
	else:
		posting = partial(context.bot.send_message, text=text)

	retry = []
	for channel_id in channels:
		try:
			posting(channel_id)
		except Unauthorized:
			context.bot_data['channels'].replace(channel_id, None)
			logging.info("Bot was removed from channel %s.", channel_id)
		except ChatMigrated as err:
			context.bot_data['channels'].replace(channel_id, err.new_chat_id)
			logging.info("Channel %s migrated to %s.", channel_id, err.new_chat_id)
			retry.append(err.new_chat_id)
		except BadRequest as err:
			if str(err) == "Chat not found":
				context.bot_data['channels'].replace(channel_id, None)
			elif str(err) != "Need administrator rights in the channel chat":
				retry.append(channel_id)
			logging.warning("Channel %s bad request: %s.", channel_id, err)
		except Exception as err:  # pylint: disable=broad-except
			logging.warning("Channel %s error (%s): %s.", channel_id, type(err), err)
			retry.append(channel_id)

	if not retry:
		logging.info("Posting <%s> done successfully!", context.job.name)
	elif retries > 5:
		logging.error("Giving up <%s>, %s left unposted.", context.job.name, retry)
	else:
		delay = 2 ** retries
		logging.warning("Retry <%s> in %s minutes.", context.job.name, delay)
		sleep(delay * 60)
		post_to_channels(context, retry, retries + 1)


def schedule_posts(job_queue, posts):
	job_queue.scheduler.remove_all_jobs()
	for iso_time, text, tg_image_id in posts:
		when = datetime.fromisoformat(iso_time)
		job_queue.run_once(post_to_channels, when, (text, tg_image_id), iso_time)
	logging.info("Scheduled %s posts.", len(posts))
