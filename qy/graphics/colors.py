def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv / 3], 16) for i in range(0, lv, lv / 3))


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb


def brighter(color):
    rgb = hex_to_rgb(color)
    p = 0.7
    rgb = tuple(map(lambda x: (255 * p + x * (1 - p)), rgb))
    return rgb_to_hex(rgb)


def bit_brighter(color):
    rgb = hex_to_rgb(color)
    p = 0.2
    rgb = tuple(map(lambda x: (255 * p + x * (1 - p)), rgb))
    return rgb_to_hex(rgb)

colors = ['#113F8C',  '#D70060', '#01A4A4',
          '#E54028', '#D0D102', '#32742C', '#F18D05', '#616161']
colors = map(bit_brighter, colors)
colors_rgb = map(hex_to_rgb, colors)
pastels = [brighter(color) for color in colors]
pastels_rgb = map(hex_to_rgb, pastels)


def get_color(n):
    return colors[n % len(colors)]


def get_color_rgb(n):
    return colors_rgb[n % len(colors)]


def get_pastel(n):
    return pastels[n % len(pastels)]


def get_pastel_rgb(n):
    return pastels_rgb[n % len(pastels)]
