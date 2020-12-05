"""Get posts from Excel file."""

from datetime import date, datetime, time

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException


class ParseError(Exception):
	"""Indicates error in Excel file."""


def parse_document(file):
	try:
		document = load_workbook(file, read_only=True)
	except OSError as err:
		raise ParseError("Ошибка чтения файла.") from err
	except InvalidFileException as err:
		raise ParseError("Невалидный файл.") from err

	posts = []
	for row in document.active.iter_rows(min_row=2, min_col=2, max_col=7):
		try:
			date_cl, time_cl, title_cl, body_cl, points_cl, image_cl = tuple(row)
		except ValueError as e:
			raise ParseError(f"Недостаточно данных в строке {len(posts) + 1}.") from e

		if not isinstance(date_cl.value, date):
			raise ParseError(f"В ячейке {date_cl.coordinate} должна быть дата.")
		if not isinstance(time_cl.value, time):
			raise ParseError(f"В ячейке {time_cl.coordinate} должно быть время.")
		timestamp = datetime.combine(date_cl.value, time_cl.value)

		if not title_cl.value:
			raise ParseError(f"В ячейке {title_cl.coordinate} должен быть заголовок.")
		post_text = f"*{title_cl.value}*"
		if body_cl.value:
			post_text += f"\n\n{body_cl.value}"
		if points_cl.value:
			post_text += "\n\n" + "\n".join(
				"✔️" + line for line in str(points_cl.value).splitlines() if line)

		posts.append((timestamp, post_text, image_cl.value))

	return posts
