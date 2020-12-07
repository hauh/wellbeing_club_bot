"""Customized Bot."""

from telegram import Bot, ParseMode
from telegram.ext.messagequeue import MessageQueue, queuedmessage
from telegram.utils.request import Request

PARSE_MODE = ParseMode.MARKDOWN


class WellbeingClubBot(Bot):
	"""Organizes mass messaging through MessageQueue to avoid hitting flood
	limits. Cleans chat when in conversation."""

	def __init__(self, *args, **kwargs):
		super().__init__(
			*args,
			request=Request(con_pool_size=10, read_timeout=10),
			**kwargs
		)
		self._is_messages_queued_default = True
		self._msg_queue = MessageQueue(
			all_burst_limit=28,
			all_time_limit_ms=1050,
			group_burst_limit=19,
			group_time_limit_ms=63000
		)

	def __del__(self):
		self._msg_queue.stop()

	@queuedmessage
	def send_message(self, *args, parse_mode=PARSE_MODE, **kwargs):
		return super().send_message(*args, parse_mode=parse_mode, **kwargs)

	@queuedmessage
	def send_photo(self, *args, parse_mode=PARSE_MODE, **kwargs):
		return super().send_photo(*args, parse_mode=parse_mode, **kwargs)
