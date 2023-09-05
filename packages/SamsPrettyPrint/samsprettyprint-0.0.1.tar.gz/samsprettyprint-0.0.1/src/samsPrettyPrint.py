import math
from typing import List

"""
Many useful functions to format prints neatly
"""

# Enable if IDE can use ASCII color codes such as \033[91m
AsciiColorCodesEnabled = True


def printTable(rows: List, column_titles=None, separator='   ', maxChar=50):
	"""
	Prints data neatly as a table
	:param rows: A list of rows. Each row should be a list of elements to be printed sequentially
	:param column_titles: A list of strings to be printed at the top of each column
	:param separator: The characters that should fill the gaps between columns
	:param maxChar: No cell will exceed a width of maxChar
	"""

	# If titles are provided, we simply add them as the first row
	if column_titles:
		rows = [column_titles] + rows

	# The number of columns is the lengths of the longest row
	number_of_columns = max([len(row) for row in rows])

	# Iterate over rows one by one
	for row in rows:

		# Fill missing elements with blanks
		while len(row) < number_of_columns:
			row.append("")

		# Cast all items to strings and restrict it's length to at most maxChar
		for c in range(number_of_columns):
			row[c] = str(row[c])[:maxChar]

	# We store the width of the widest cell in each column
	column_width = [
		max([len(removeColorTags(row[c])) for row in rows]) for c in range(number_of_columns)
	]

	# Enumerate the rows
	for r, row in enumerate(rows):

		# Format each cell to add spaces where it is shorter than the column width
		items = [row[c] + ' '*(column_width[c] - len(removeColorTags(row[c]))) for c in range(number_of_columns)]

		# Join the cells with the separator
		print(separator.join(items))

		# If we have titles, print a lines of dashes under the titles to underline them.
		if column_titles and r == 0:
			print(separator.join(['-'*column_width[c] for c in range(number_of_columns)]))


def printDict(dictionary: dict, indentation='   • ', separator='   ', keyTitle='', valueTitle='', forcedKeyWidth=None):
	"""
	Prints a dictionary with neat spacing
	:param dictionary: {key: value} where both keys and values can be cast to a string
	:param indentation: The indentation will be printed before each line
	:param separator: The separator will be printed between the key and value
	:param keyTitle: If provided will be printed above the column of keys with a --- underline
	:param valueTitle: If provided will be printed above the column of keys with a --- underline
	:param forcedKeyWidth: Forces each key to fill exactly this many characters
	:return:
	"""

	# Find the maximum character width of the keys and values
	maxKeyWidth = max([len(str(key)) for key in dictionary.keys()] + [len(keyTitle)])
	maxValueWidth = max([len(str(value)) for value in dictionary.values()] + [len(valueTitle)])

	# The user may force the width to some value
	if forcedKeyWidth:
		maxKeyWidth = forcedKeyWidth

	# If titles are provided print them with a dashed line underneath
	if keyTitle or valueTitle:
		print(f"{indentation}{str(keyTitle)[:maxKeyWidth]}{' ' * (maxKeyWidth - len(str(keyTitle)))}{separator}{str(valueTitle)}")
		print(f"{' ' * len(indentation)}{'-' * maxKeyWidth}{separator}{'-' * maxValueWidth}")

	# Print out the keys and values line by line
	for key, value in dictionary.items():
		print(f"{indentation}{str(key)[:maxKeyWidth]}{' ' * (maxKeyWidth - len(str(key)))}{separator}{str(value)}")


def errorRed(text: str):
	if AsciiColorCodesEnabled:
		print("\033[91m" + "ERROR: " + text + "\033[0m")
	else:
		print("ERROR: " + text)


def warningOrange(text: str):
	if AsciiColorCodesEnabled:
		print("\033[93m" + "WARNING: " + text + "\033[0m")
	else:
		print("WARNING: " + text)


def failRed(text: str):
	if AsciiColorCodesEnabled:
		print("\033[91m" + "❌ " + text + "\033[0m")
	else:
		print("ERROR: " + text)


def passGreen(text: str):
	if AsciiColorCodesEnabled:
		print("\033[92m" + "✔ " + text + "\033[0m")
	else:
		print("PASS: " + text)


def printTitle(title: str, width=54):
	"""
	Prints out the provided title in bold font and surrounded buy bars.
	If a width is provided, it will fill that number of characters.
	"""
	centreWidth = width - 4

	# The print. Note \033[1m is the ANSI escape sequence for bold
	print("\n")
	print(r'//' + '=' * centreWidth + r'\\')
	print(r'||' + '\033[1m' + title.center(centreWidth) + '\033[0m' + r'||')
	print(r'\\' + '=' * centreWidth + r'//')


def removeColorTags(text: str) -> str:
	for tag in [
		"\033[91m",
		"\033[92m",
		"\033[93m",
		'\033[1m',
		"\033[0m"
	]:
		text = text.replace(tag, '')
	return text