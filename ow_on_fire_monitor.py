from pyautogui import screenshot, locateOnScreen
from ctypes import windll

import color_utils

# Split on-fire meter in this many parts
FRAGMENTS_COUNT = 10

# The on-fire meter is blue when it's low and white when it's filled
VALID_COLORS = [
	(89, 221, 224), # low
	(138, 226, 226), # middle
	(231, 231, 231) # high
]

MAX_COLOR_DIFFERENCE = 100

fragment_positions = {}
background_positions = []

last_values = [(0, 1)]

def get_on_fire_value(screenshot):
	"""Gets the value on the 'on-fire meter', which represents the players performance"""

	# Calculate positions to check
	gen_fragment_positions()

	# Check positions until not filled
	percentage = 0
	for fragment_position in fragment_positions:
		color = screenshot.getpixel((fragment_positions[fragment_position][0], fragment_positions[fragment_position][1]))
		if is_meter_color(color):
			percentage = fragment_position
		else:
			break

	# Get background color to check reliability of read value
	background_points_valid = 0
	for background_position in background_positions:
		color = screenshot.getpixel((background_position[0], background_position[1]))
		if not is_meter_color(color):
			background_points_valid += 1
	reliability = background_points_valid / len(background_positions)
	reliability = min(max(reliability, 0.1), 0.9) # Cap to 0.1 < reliability < 0.9

	# Calculate average to minimize effect of wrong detected values
	last_values.append((percentage, reliability))
	if len(last_values) > 3:
		last_values.pop(0)
	total_reliability = 0
	total_percentage = 0
	for last_value in last_values:
		total_percentage += last_value[0] * last_value[1]
		total_reliability += last_value[1]
	average_reliability = total_reliability / len(last_values)
	average_percentage = (total_percentage / len(last_values)) / average_reliability

	return round(average_percentage, 2)

def is_meter_color(color):
	return any(color_utils.get_color_difference(valid_color, color) < MAX_COLOR_DIFFERENCE for valid_color in VALID_COLORS)

def gen_fragment_positions():
	"""Calculates the check-positions on the on-fire meter"""

	if len(fragment_positions) > 0:
		return
	
	# Start/End postion of the on-fire meter on a 2560 x 1440 px screen
	ref_size = (2560, 1440)
	min_position_ref = (380, 1324)
	max_position_ref = (580, 1312)

	# Calculate position for actual screensize
	user32 = windll.user32
	screen_x, screen_y = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
	x_factor = screen_x / ref_size[0]
	y_factor = screen_y / ref_size[1]
	min_position = (round(min_position_ref[0] * x_factor), round(min_position_ref[1] * y_factor))
	max_position = (round(max_position_ref[0] * x_factor), round(max_position_ref[1] * y_factor))
	width = max_position[0] - min_position[0]
	height = max_position[1] - min_position[1]

	# Calculate steps between min and max
	for i in range(1, FRAGMENTS_COUNT + 1):
		percentage = i / FRAGMENTS_COUNT
		fragment_positions[percentage] = (min_position[0] + width * percentage, min_position[1] + height * percentage)

	# Calculate points where the background is visible
	background_refs = [
		(430, 1350),
		(560, 1230),
		(670, 1300)
	]
	for background_ref in background_refs:
		background_positions.append((round(background_ref[0] * x_factor), round(background_ref[1] * y_factor)))
