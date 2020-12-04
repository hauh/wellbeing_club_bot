"""Get posts from Excel file."""

from datetime import datetime

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
	for row in document.active.iter_rows(min_row=2, max_col=4):
		dt_cell, text_cell, image_cell, url_cell = tuple(row)
		if not isinstance(dt_cell.value, datetime):
			raise ParseError(f"В ячейке {dt_cell.coordinate} должна быть дата.")
		post_text = f"{text_cell.value}\n\n[ссылка]({url_cell.value})"
		posts.append((dt_cell.value, post_text, image_cell.value))

	return posts
