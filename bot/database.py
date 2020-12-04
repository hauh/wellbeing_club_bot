"""Database manager."""

import logging
import sqlite3


class Database:
	"""SQLite3 database manager."""

	def __init__(self):
		self.connection = sqlite3.connect('wellbeing.db')
		self.transact(
			"""
			CREATE TABLE if not exists 'users' (
				'id' INTEGER primary key,
				'username' TEXT,
				'subscribed' INTEGER default 1,
				'subscription_time' TEXT default CURRENT_TIMESTAMP,
				'posts_seen' INTEGER default 0,
				'cancellation_time' TEXT
			)
			"""
		)
		self.transact(
			"""
			CREATE TABLE if not exists 'posts' (
				'id' INTEGER primary key,
				'posted' INTEGER default 0,
				'timestamp' INTEGER unique,
				'body' BLOB,
				'image' TEXT
			)
			"""
		)
		logging.info('Database connected.')

	def __del__(self):
		self.connection.close()

	def transact(self, query, params=()):
		try:
			with self.connection as connection:
				return connection.execute(query, params)
		except sqlite3.DatabaseError as err:
			logging.error('Database error! - %s', err)

	def subscribe(self, user_id, username):
		self.transact(
			"""
			INSERT INTO users (id, username) VALUES (?, ?)
			ON CONFLICT (id) DO UPDATE SET
				username = excluded.username,
				subscribed = 1,
				cancellation_time = null
			""",
			(user_id, username)
		)
		logging.info('New subscriber! - %s (%s).', username, user_id)

	def cancel_subscription(self, user_id):
		self.transact(
			"""
			UPDATE users SET
				subscribed = 0,
				cancellation_time = CURRENT_TIMESTAMP
			WHERE id = ?
			""",
			(user_id,)
		)
		logging.info('User %s cancelled subscription.', user_id)

	def get_users(self):
		return self.transact("SELECT id FROM users WHERE subscribed = 1").fetchall()

	def save_post(self, timestamp, post, image):
		return self.transact(
			"""
			INSERT INTO posts (timestamp, body, image) VALUES (?, ?, ?)
			ON CONFLICT (timestamp) DO UPDATE SET
				body = excluded.body,
				image = excluded.image
			""",
			(timestamp, post, image)
		).lastrowid

	def posted(self, post_id):
		users_count = self.transact(
			"UPDATE users SET posts_seen = posts_seen + 1 WHERE subscribed = 1"
		).rowcount
		self.transact(
			"UPDATE posts SET posted = posted + ? WHERE id = ?",
			(users_count, post_id)
		)

	def posts_stats(self):
		return self.transact("SELECT id, posted FROM posts").fetchall()

	def _test(self):
		for i in range(10):
			self.subscribe(i, str(i))
		subscribed = self.get_users()
		assert len(subscribed) == 10, len(subscribed)
		for i in range(5):
			self.cancel_subscription(i)
		subscribed = self.get_users()
		assert len(subscribed) == 5, len(subscribed)
		post_id = self.save_post("CURRENT_TIMESTAMP", "post", 'image_path')
		self.posted(post_id)
		stats = self.posts_stats()
		assert len(stats) == 1, len(stats)
		assert stats[0][1] == 5, stats[0]
