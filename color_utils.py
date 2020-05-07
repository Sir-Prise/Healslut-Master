def get_color_difference(color1, color2):
	color1_r, color1_g, color1_b = color1
	color2_r, color2_g, color2_b = color2
	return abs(color1_r - color2_r) + abs(color1_g - color2_g) + abs(color1_b - color2_b)

def get_closest_color(colors, color, max_difference = None):
    best_color_difference = None
    best_color = None
    for check_color in colors:
        difference = get_color_difference(color, check_color)
        if (max_difference is None or difference <= max_difference) and (best_color_difference is None or best_color_difference > difference):
            best_color_difference = difference
            best_color = check_color

    if best_color is not None:
        return best_color
    
    raise Exception('No close color found', color)