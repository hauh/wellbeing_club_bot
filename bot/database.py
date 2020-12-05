"""Database manager."""

import logging
import sqlite3
from threading import Lock


class Database:
	"""SQLite3 database manager."""

	SQLITE_LIMIT_VARIABLE_NUMBER = 500

	def __init__(self, db_name):
		self.connection = sqlite3.connect(
			db_name,
			check_same_thread=False,
			detect_types=sqlite3.PARSE_DECLTYPES
		)
		self.lock = Lock()
		self.transact(
			"""
			CREATE TABLE if not exists 'users' (
				'id' INTEGER primary key,
				'username' TEXT,
				'subscribed' INTEGER default 1,
				'subscription_time' TIMESTAMP default CURRENT_TIMESTAMP,
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
				'timestamp' TIMESTAMP unique,
				'body' BLOB,
				'image' TEXT
			)
			"""
		)
		logging.info('Database connected.')

	def __del__(self):
		self.connection.close()

	def transact(self, query, params=()):
		with self.lock:
			try:
				with self.connection as connection:
					return connection.execute(query, params)
			except sqlite3.DatabaseError as err:
				logging.error('Database error! - %s', err)
				raise

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
		logging.info('New subscriber! - %s (id %s).', username, user_id)

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

	def check_subscription(self, user_id):
		user = self.transact(
			"SELECT subscribed FROM users WHERE id = ?",
			(user_id,)
		).fetchone()
		if not user or not user[0]:
			return False
		return True

	def get_users(self):
		return self.transact("SELECT id FROM users WHERE subscribed = 1").fetchall()

	def get_posts(self):
		return self.transact(
			"""
			SELECT timestamp, body, image FROM posts
			WHERE timestamp > date('now')
			"""
		).fetchall()

	def save_posts(self, posts):
		for timestamp, post, image in posts:
			self.transact(
				"""
				INSERT INTO posts (timestamp, body, image) VALUES (?, ?, ?)
				ON CONFLICT (timestamp) DO UPDATE SET
					body = excluded.body,
					image = excluded.image
				""",
				(timestamp, post, image)
			)

	def posted(self, post_id, chats):
		for i in range(len(chats) // self.SQLITE_LIMIT_VARIABLE_NUMBER + 1):
			chunk = chats[
				i * self.SQLITE_LIMIT_VARIABLE_NUMBER:
				(i + 1) * self.SQLITE_LIMIT_VARIABLE_NUMBER
			]
			self.transact(
				"UPDATE users SET posts_seen = posts_seen + 1 WHERE id IN ({})"
				.format(', '.join(chunk))
			)
		self.transact(
			"UPDATE posts SET posted = posted + ? WHERE timestamp = ?",
			(len(chats), post_id)
		)

	def posts_stats(self):
		return self.transact("SELECT timestamp, posted FROM posts").fetchall()

	def _test(self):
		for i in range(10):
			self.subscribe(i, str(i))
		subscribed = self.get_users()
		assert len(subscribed) == 10, len(subscribed)
		for i in range(5):
			self.cancel_subscription(i)
		assert self.check_subscription(1) is False
		assert self.check_subscription(6) is True
		subscribed = self.get_users()
		assert len(subscribed) == 5, len(subscribed)
		self.save_posts((("1212-12-12 12:12:12", "post", 'image_path'),))
		self.SQLITE_LIMIT_VARIABLE_NUMBER = 2
		print(self.transact('select * from posts').fetchall())
		self.posted("1212-12-12 12:12:12", ('5', '6', '7', '8', '9'))
		stats = self.posts_stats()
		assert len(stats) == 1, len(stats)
		assert stats[0][1] == 5, stats[0]
