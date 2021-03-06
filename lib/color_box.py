from .png import Writer
from .rgba import RGBA
import base64
import io

CHECK_LIGHT = "#FFFFFF"
CHECK_DARK = "#CCCCCC"

LIGHT = 0
DARK = 1


def split_channels(rgb):
    """
    Take a color of the format #RRGGBBAA (alpha optional and will be stripped)
    and convert to a list with format [r, g, b].
    """
    return [
        int(rgb[1:3], 16),
        int(rgb[3:5], 16),
        int(rgb[5:7], 16)
    ]


def checkered_color(color, background):
    """ Mix color with the checkered color """
    checkered = RGBA(color)
    checkered.apply_alpha(background)
    return checkered.get_rgb()


def color_box(color, border, size=16, border_size=1, check_size=4):
    """
    Create an RGBA color box with the specified RGBA color
    and RGB(A) border (alpha will be stripped out of border color).

    Define size of swatch, border width,  and size of checkered board squares.
    """
    assert size - (border_size * 2) >= 0, "Border size too big!"

    # Create bytes buffer for png
    f = io.BytesIO()

    # Mix transparent color with checkered colors
    # And covert colors to to lists containing r, g, b channels
    light = split_channels(checkered_color(color, CHECK_LIGHT))
    dark = split_channels(checkered_color(color, CHECK_DARK))
    border = split_channels(border)

    # Size of color swatch between borders
    color_size = size - (border_size * 2)

    # Draw borders and create the checkered
    # pattern with the mixed light and dark colors
    p = [border * size]
    check_color_y = DARK
    for y in range(0, color_size):
        if y % check_size == 0:
            check_color_y = DARK if check_color_y == LIGHT else LIGHT
        row = list(border * border_size)
        check_color_x = check_color_y
        for x in range(0, color_size):
            if x % check_size == 0:
                check_color_x = DARK if check_color_x == LIGHT else LIGHT
            row += (dark if check_color_x == DARK else light)
        row += border * border_size
        p.append(row)
    p.append(border * size)

    # Write out png
    img = Writer(size, size)
    img.write(f, p)

    # Read out png bytes and base64 encode
    f.seek(0)
    return "<img src=\"data:image/png;base64,%s\">" % (
        base64.b64encode(f.read()).decode('ascii')
    )


def palette_preview(colors, border, height=32, width=32 * 8, border_size=1, check_size=4):
    assert height - (border_size * 2) >= 0, "Border size too big!"
    assert width - (border_size * 2) >= 0, "Border size too big!"

    # Gather preview colors
    border = split_channels(border)
    preview_colors = []
    count = 5 if len(colors) >= 5 else len(colors)

    if count:
        for c in range(0, count):
            preview_colors.append(
                (
                    split_channels(checkered_color(colors[c], CHECK_LIGHT)),
                    split_channels(checkered_color(colors[c], CHECK_DARK))
                )
            )
    else:
        preview_colors.append(
            (split_channels(CHECK_LIGHT), split_channels(CHECK_DARK))
        )

    color_height = height - (border_size * 2)
    color_width = width - (border_size * 2)

    if count:
        dividers = int(color_width / count)
        if color_width % count:
            dividers += 1
    else:
        dividers = 0

    color_size_x = width - (border_size * 2)
    p = [border * width]
    check_color_y = DARK
    for y in range(0, color_height):
        index = 0
        if y % check_size == 0:
            check_color_y = DARK if check_color_y == LIGHT else LIGHT
        row = list(border * border_size)
        check_color_x = check_color_y
        for x in range(0, color_size_x):
            if x != 0 and dividers != 0 and x % dividers == 0:
                index += 1
            if x % check_size == 0:
                check_color_x = DARK if check_color_x == LIGHT else LIGHT
            row += (preview_colors[index][1] if check_color_x == DARK else preview_colors[index][0])
        row += border * border_size
        p.append(row)
    p.append(border * width)

    # Create bytes buffer for png
    f = io.BytesIO()

    # Write out png
    img = Writer(width, height)
    img.write(f, p)

    # Read out png bytes and base64 encode
    f.seek(0)
    return "<img src=\"data:image/png;base64,%s\">" % (
        base64.b64encode(f.read()).decode('ascii')
    )
