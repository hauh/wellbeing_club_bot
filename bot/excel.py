"""Get posts from Excel file."""

from datetime import date, datetime, time

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException


class ParseError(Exception):
	"""Indicates error in Excel file."""


def parse_document(file):
	try:
		document = load_workbook(file)
	except (OSError, IOError) as e:
		raise ParseError("Ошибка чтения файла.") from e
	except InvalidFileException as e:
		raise ParseError("Невалидный файл.") from e

	images = {}
	# pylint: disable=protected-access
	for image in document.active._images:
		row = image.anchor._from.row
		if row in images:
			raise ParseError(f"Несколько изображений в строке {row}.")
		image.ref.seek(0)
		images[row] = image.ref

	posts = []
	row_number = 1
	for row in document.active.iter_rows(min_row=2, min_col=2, max_col=6):
		row_number += 1
		try:
			date_cell, time_cell, title_cell, body_cell, points_cell = tuple(row)
		except ValueError as e:
			raise ParseError(f"Ошибка чтения данных (строка {row_number}).") from e

		if not isinstance(date_cell.value, date):
			raise ParseError(f"В ячейке {date_cell.coordinate} должна быть дата.")
		if not isinstance(time_cell.value, time):
			raise ParseError(f"В ячейке {time_cell.coordinate} должно быть время.")
		timestamp = datetime.combine(date_cell.value, time_cell.value)

		if not title_cell.value:
			raise ParseError(f"В ячейке {title_cell.coordinate} должен быть заголовок.")
		post_text = f"*{title_cell.value}*"
		if body_cell.value:
			post_text += f"\n\n{body_cell.value}"
		if points_cell.value:
			post_text += "\n\n" + "\n".join(
				"✔️" + line for line in str(points_cell.value).splitlines() if line)

		posts.append([timestamp, post_text, images.get(row_number)])

	return posts
