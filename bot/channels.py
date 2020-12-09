"""Helpers for tracking channels."""

import json
import logging

from telegram.constants import CHAT_CHANNEL
from telegram.ext import Handler

from bot import CHANNELS_FILE


class ChannelsRegistrator(Handler):
	"""Registers new channels for messaging to them later."""

	def __init__(self):
		super().__init__(callback=None)

	def check_update(self, update):
		chat = update.effective_chat
		if chat and chat.type == CHAT_CHANNEL:
			return chat
		return False

	def handle_update(self, _update, _dispatcher, channel, context):
		channels = context.bot_data['channels']
		if channel.id not in channels:
			channels.add(channel.id)
			logging.info("New channel found (%s).", channel.title or channel.id)


class ChannelsCollection:
	"""Collects and persists known channels."""

	def __init__(self):
		try:
			with open(CHANNELS_FILE, 'r') as f:
				self.items = set(json.load(f))
		except (FileNotFoundError, json.JSONDecodeError):
			self.items = set()

	def __iter__(self):
		return iter(self.items)

	def add(self, new_channel_id):
		if new_channel_id not in self.items:
			self.items.add(new_channel_id)
			self._save()

	def replace(self, old_channel_id, new_channel_id):
		self.items.discard(old_channel_id)
		if new_channel_id:
			self.items.add(new_channel_id)
		self._save()

	def _save(self):
		with open(CHANNELS_FILE, 'w') as f:
			json.dump(tuple(self.items), f)
