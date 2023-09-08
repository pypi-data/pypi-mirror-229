"""

Drawing Operations
==================

pythonGraph's drawing routines can output a variety of shapes in a variety of
colors.

Before using these operations, please note that:

* `open_window` must be called first, otherwise a run-time error will
  occur.
* You must call update_window before the result of the drawing routines will be
  visible on the screen.

Mouse Operations
================

pythonGraph can determine the current location of the mouse.  It can also
determine whether or not a mouse click has occurred.

Before using these operations, please note that:

* `open_window` must be called first, otherwise a run-time error will occur.
* The window must be in focus. If the pythonGraph window is not on top, the
  user may have to click on it once before the application will respond to user
  mouse clicks.

"""

import collections
import math
import random

import pygame


# Pygame Window
win = None

# Pygame events
event_list = []

# Pygame Font ('None' will use the system default)
font = None

# Cache (Used to Prevent Loading the Same Media Multiple Times)
images = {}
sounds = {}

# Mouse Constants
mouse_lookup = {
    "LEFT": 1,
    "CENTER": 2,
    "RIGHT": 3,
}

MouseButton = collections.namedtuple('MouseButton',
                                     ['LEFT', 'RIGHT', 'CENTER'])
mouse_buttons = MouseButton(
    LEFT=mouse_lookup['LEFT'],
    CENTER=mouse_lookup['CENTER'],
    RIGHT=mouse_lookup['RIGHT'])


# Window Operations
def open_window(width, height):
    '''Creates a graphics window of the specified width and height (in pixels).

    .. note:: You can only have one pythonGraph window open at a time. If you
              attempt to open a second, an error will occur.

    .. note:: The `width` and `height` dimensions cannot be negative.

    The following code snippet opens a 400x300-pixel window:

    .. code-block:: python

        pythonGraph.open_window(400, 300)

    '''
    global win
    pygame.init()
    pygame.mixer.init()
    win = pygame.display.set_mode((width, height))
    clear_window('white')
    set_window_title('pythonGraph')


def close_window():
    '''Closes the pythonGraph window.

    An error is raised if the graphics window is not open.

    .. code-block:: python

        pythonGraph.close_window()

    '''
    quit()


def clear_window(color):
    '''Clears the entire window to a particular color.

    `color` can either be a predefined value or a custom color created using
    the `create_color` or `create_random_color` functions.

    .. code-block:: python

        pythonGraph.clear_window("red")

    '''
    win.fill(color)


def get_window_height():
    width, height = pygame.display.get_surface().get_size()
    return height


def get_window_width():
    width, height = pygame.display.get_surface().get_size()
    return width


def set_window_title(title):
    pygame.display.set_caption(title)


def update_window(refresh_rate=33):
    global event_list
    if win is not None:
        pygame.event.pump()
        del event_list[:]
        pygame.display.update()
        delay(refresh_rate)


# Colors Operations
def create_color(red, green, blue):
    return (red, green, blue)


def create_random_color():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    return (red, green, blue)


def get_color(x, y):
    return pygame.display.get_surface().get_at((x, y))


# Drawing Operations
def _get_rectangle(x1, y1, x2, y2):
    # Assumes that we were given top left / bottom right coordinates (we verify
    # this later)
    top_left_x = x1
    top_left_y = y1
    bottom_right_x = x2
    bottom_right_y = y2

    # Adjusts the coordinates provided so that we know the top left and bottom
    # right
    if y2 < y1:
        top_left_y = y2
        bottom_right_y = y1

    if x2 < x1:
        top_left_x = x2
        bottom_right_x = x1

    return pygame.Rect(top_left_x,
                       top_left_y,
                       bottom_right_x - top_left_x + 1,
                       bottom_right_y - top_left_y + 1)


def draw_arc(x1, y1, x2, y2, start_x, start_y, end_x, end_y, color, width=2):
    """Draw an arc

    Draws the portion of an ellipse that is inscribed inside the given
    rectangle.

    The parameters `(x1, y1)` and `(x2, y2)` represent the two opposite corners
    of the rectangle.

    The arc begins at the intersection of the ellipse and the line passing
    through the center of the ellipse and `(start_x, start_y)`. It then
    proceeds counter-clockwise until it reaches the intersection of the ellipse
    and the line passsing through the center of the ellipse to `(end_x,
    end_y)`.

    `color` can either be a predefined value or a custom color created using
    the `create_color` or `create_random_color` functions.

    `width` is an optional parameter that specifies the "thickness" of the arc
    in pixels. Otherwise, it uses a default value of 2.

    .. code-block:: python

        pythonGraph.open_graph_window(400, 300)
        pythonGraph.draw_arc(1, 100, 200, 1, 250, 50, 2, 2, "blue", 3)

    """
    # Creates the bounding rectangle (the rectangle that the arc will reside
    # within
    r = _get_rectangle(int(x1), int(y1), int(x2), int(y2))

    # Calculates the Starting Angle
    start_a = start_x - r.centerx
    start_b = start_y - r.centery
    start_angle = math.atan2(start_b, start_a) * -1.0

    # Calculates the Ending Angle
    end_a = end_x - r.centerx
    end_b = end_y - r.centery
    # the negative makes the arc go counter-clockwise like Raptor
    end_angle = math.atan2(end_b, end_a) * -1.0

    pygame.draw.arc(win, color, r, start_angle, end_angle, int(width))


def draw_circle(x, y, radius, color, filled, width=2):
    """Draw a circle

    Draws a circle at `(x, y)` with the specified radius.

    `color` specifies the circle's color. This can either be a predefined value
    or a custom color created using the create_color function.

    `filled` can be either `True` or `False`, depending on whether or not the
    circle should be filled in or not, respectively.

    `width` is an optional parameter that specifies the width of the circle's
    border. If this value is not provided, a default valueof 2will be
    used.This parameter will be ignoredif `filled` is `True`.

    .. code-block:: python

        pythonGraph.open_window(400, 300)
        pythonGraph.draw_cirlce(200, 150, 50, "green", True)

    """
    global win
    if filled:
        pygame.draw.circle(win, color, [int(x), int(y)], int(radius), 0)
    else:
        pygame.draw.circle(win, color, [int(x), int(y)], int(radius),
                           int(width))


def draw_ellipse(x1, y1, x2, y2, color, filled, width=2):
    """Draw an ellipse

    Draws anellipse inscribed in the rectangle whose two diagonally opposite
    corners, `(x1, y1)`, `(x2, y2)` are given.

    `color` can either be a predefined value or a custom color created using
    the `create_color` or `create_random_color` functions.

    `filled` can be `True` or `False`, depending on whether or not the ellipse
    is filled in or not, respectively.

    `width` is an optional parameter that specifies the width of the ellipse's
    border. If this value is not provided, a default value of 2 will be used.

    .. code-block:: python

        pythonGraph.open_window(400, 300)
        pythonGraph.draw_ellipse(100, 100, 300, 200, "blue", False, 4)

    """
    global win
    r = _get_rectangle(int(x1), int(y1), int(x2), int(y2))
    if filled:
        pygame.draw.ellipse(win, color, r, 0)
    else:
        pygame.draw.ellipse(win, color, r, int(width))


def draw_image(filename, x, y, width, height, rotation=0, centered=False):
    """Draws an image in the pythonGraph window.

    `filename` refers to the name of the file (e.g., "image.png") to be drawn.
    You can use any BMP, JPEG, or PNG file. *The image file should be in the
    same folder as your Python script.*

    `x` and `y` specify the upper-left coordinate where the image is to be
    drawn.

    `width` and `height` represent the desired dimensions of the image.
    pythonGraph will try to scale the image to fit within these dimensions.

    'rotation' is an optional parameter that will rotate the image by the given
    number of degrees in a clockwise direction

    'centered' is an optional parameter that will center the image on the
    coordinates provided if the user sets it to True.  When False by default,
    the image will be drawn with the top left corner at the provided
    coordinates

    For the following example, assume that the file "falcon.png" exists.

    .. code-block:: python

        pythonGraph.open_graph_window(400, 300)
        pythonGraph.draw_image("falcon.png", 100, 100, 150, 150)
        pythonGraph.draw_image("falcon.png", 100, 100, 150, 150, 45)
        pythonGraph.draw_image("falcon.png", 100, 100, 150, 150, 45, True)
        pythonGraph.draw_image("falcon.png", 100, 100, 150, 150, centered=True)

    """
    global win
    _load_image(filename)
    image = pygame.transform.scale(images[filename], (int(width), int(height)))

    if (rotation != 0):
        image = pygame.transform.rotate(image, -rotation)

    if (centered):
        x -= width / 2
        y -= height / 2

    win.blit(image, (x, y))


def draw_line(x1, y1, x2, y2, color, width=2):
    """Draws a line segment from `(x1, y1)` to `(x2, y2)`.

    `color` can either be a predefined value or a custom color created using
    the `create_color` or `create_random_color`

    `width` is an optional parameter that specified the width of the line. If
    this value is not provided, a default value of 2 will be used.

    .. code-block:: python

        pythonGraph.open_window(400, 300)
        pythonGraph.draw_line(50, 50, 300, 250, "blue", 3)

    """
    global win
    pygame.draw.line(win, color, (int(x1), int(y1)), (int(x2), int(y2)),
                     int(width))


def draw_pixel(x, y, color):
    """Changes the color of a single pixel at location `(x, y)`.

    `color` can either be a predefined value or a custom color breated using
    the `create_color` or `create_random_color` functions.

    .. code-block:: python

        pythonGraph.open_window(400, 300)
        pythonGraph.draw_pixel(50, 50, "red")
    """
    global win
    win.set_at((int(x), int(y)), color)


def draw_rectangle(x1, y1, x2, y2, color, filled, width=2):
    """Draw a rectangle

    Draws a rectangle on the screen.

    `(x1, x2)` is any corner of the rectangle

    `(x2, y2)` is the opposite corner of the rectangle

    `color` specifies the rectangle's color. This can either be a predefined
    value or a custom color created using the `create_color` function.

    `filled` can be either `True` or `False`, depending on whether or not the
    rectangle should be filled in or not, respectively.

    `width` is an optional parameter that specifies the width of the
    rectangle's border.  If this value is not provided, a default value will be
    used.

    .. code-block:: python

        pythonGraph.open_window(400, 300)
        pythonGraph.draw_rectangle(50, 150, 250, 25, "red", True)

    """
    global win
    r = _get_rectangle(int(x1), int(y1), int(x2), int(y2))
    if filled:
        pygame.draw.rect(win, color, r, 0)
    else:
        pygame.draw.rect(win, color, r, int(width))


# Text Operations
def write_text(text, x, y, color, font_size=30):
    global font
    font = pygame.font.SysFont('None', int(font_size))
    text = font.render(str(text), True, color)
    win.blit(text, (int(x), int(y)))


def draw_text(text, x, y, color, font_size=30, centered=False,
              background=None, border=None, border_width=1, padding=0):
    """Writes the specified text string to the pythonGraph window.

    `text` represents the string to be written.

    `(x, y)` denotes the coordinate of the top left corner of the string.

    `color` can either be a predefined value or a custom color breated using
    the `create_color` or `create_random_color` functions.

    `font_size` is an optional parameter that specifies the size of the text,
    in pixels. If this value is not provided, a default value of 30 will be
    used.

    `centered` is an optional parameter set to False by default to maintain
    original functionality of the function.  If set to True, the function will
    calculate where to draw the text such that it is centered on the provided
    coordinates.  If False, it will draw the text starting at the provided
    coordinates (the top left of the text).

    `background` is an optional parameter set to None by default.  If the user
    specifies a color, then the function will take the provided x and y (to
    include the adjusted coordinates if centered=True) and draw the colored box
    behind the text.

    `border` is an optional parameter set to None by default.  If the user
    specifies a color, then the function will add a border (i.e., a "frame")
    around the text.

    `border_width` is the width of the border, which is 1 pixel by default.

    `padding` is an optional parameter that dictates how much space will be
    between the text and the edge of the box.  If the default (padding=0), then
    the background will be tight around the text. If padding=5, then there will
    be a 5-pixel buffer between the box and the text

    .. code-block:: python

        pythonGraph.open_window(400, 300)
        pythonGraph.draw_text("Hello, World!", 50, 30, "red", 50)
        pythonGraph.draw_text("Hello, World!", 50, 30, "teal", centered=True)
        pythonGraph.draw_text("Hello, World!", 50, 30, "cornflowerblue",
                              centered=True, background="black")
        pythonGraph.draw_text("Hello, World!", 50, 30, "plum",
                              background="tomato")
        pythonGraph.draw_text("Hello, World!", 50, 150, "red",
                              background="tomato", border="black")
        pythonGraph.draw_text("Hello, World!", 50, 150, "plum",
                              background="tomato", padding=20)

    """

    '''
    By specifying an empty string for the font style, pygame will choose the
    default system font. For example, "arial" and "calibri" will cause the
    centered=True text to be drawn too high. "freesansbold" works perfectly,
    though.

    This may cause an issue if the user's default is arial or calibri, for
    example.
    '''
    font = pygame.font.SysFont("", font_size)

    # Size of the text in pixels
    text_width, text_height = font.size(text)

    # If the user wants to center the text on the provided coordinates
    if (centered):
        x = x - (text_width / 2)
        y = y - (text_height / 2)

    box_x2 = x + text_width + padding
    box_y2 = y + text_height + padding
    box_x1 = x - padding
    box_y1 = y - padding

    if (background is not None):
        # Calculate where to draw the rectangle to fit the text perfectly
        draw_rectangle(box_x1, box_y1, box_x2, box_y2, background, True)

    if border is not None:
        draw_rectangle(box_x1 - border_width, box_y1 - border_width,
                       box_x2 + border_width, box_y2 + border_width,
                       border, False, width=border_width)

    write_text(text, x, y, color, font_size)


# Sound
def play_sound_effect(filename):
    _load_sound(filename)
    sound = sounds[filename]
    channel = pygame.mixer.find_channel()  # Searches for an available channel
    if channel is not None:
        channel.play(sound)


def play_music(filename, loop=True):
    pygame.mixer.music.load(filename)

    if loop:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.play(1)


def stop_music():
    pygame.mixer.music.stop()


# Events (Keyboard, Mouse, Window)
def _get_events():
    global event_list
    if (len(event_list) == 0):
        event_list = pygame.event.get()
    return event_list


# Event Operations (Keyboard, Mouse, Window)
def get_mouse_x():
    x, y = pygame.mouse.get_pos()
    return x


def get_mouse_y():
    x, y = pygame.mouse.get_pos()
    return y


def _get_mouse_button(button):
    if isinstance(button, str) and str(button).upper() in mouse_lookup:
        return mouse_lookup[button.upper()]
    else:
        return button


def _get_key(key_string):
    # Removes the '[]' characters that surround some keys
    if len(key_string) > 1:
        key_string = key_string.replace("[", "")
        key_string = key_string.replace("]", "")
    return key_string


def key_pressed(which_key):
    # use lower case for consistency with pygame
    which_key = which_key.lower()

    for event in _get_events():
        if event.type == pygame.KEYDOWN:
            return _get_key(pygame.key.name(event.key)) == which_key
    return False


def key_down(which_key):
    # Gets the key codes of the pressed keys
    pressed = pygame.key.get_pressed()

    # Converts the key specified by the user into
    # the corresponding pygame key
    k = pygame.key.key_code(_get_key(which_key))

    # Returns if the specified key code is legal
    return pressed[k]


def key_released(which_key):
    # use lower case for consistency with pygame
    which_key = which_key.lower()

    for event in _get_events():
        if event.type == pygame.KEYUP:
            return _get_key(pygame.key.name(event.key)) == which_key
    return False


def mouse_button_pressed(which_button):
    for event in _get_events():
        if event.type == pygame.MOUSEBUTTONDOWN:
            return event.button == _get_mouse_button(which_button)
    return False


def mouse_button_down(which_button):
    pressed = pygame.mouse.get_pressed()
    return pressed[_get_mouse_button(which_button)-1]


def mouse_button_released(which_button):
    for event in _get_events():
        if event.type == pygame.MOUSEBUTTONUP:
            return event.button == _get_mouse_button(which_button)
    return False


def window_closed():
    if win is None:
        return True
    else:
        for event in _get_events():
            if event.type == pygame.QUIT:
                close_window()
    return win is None


def window_not_closed():
    return not window_closed()


def wait_for_close():
    while not window_closed():
        update_window()


def save_screenshot(filename):
    if win is not None:
        pygame.image.save(win, filename)
    else:
        print("Cannot Save Image")


def quit():
    global win
    win = None
    pygame.quit()


# Miscellaneous Operations
def delay(time):
    pygame.time.delay(time)


def get_pressed_key():
    for event in _get_events():
        if event.type == pygame.KEYDOWN:
            return _get_key(pygame.key.name(event.key))
    return None


def _load_image(filename):
    global images
    if filename not in images.keys():
        images[filename] = pygame.image.load(filename).convert_alpha()


def _load_sound(filename):
    global sounds
    if filename not in sounds.keys():
        sound = pygame.mixer.Sound(filename)
        sounds[filename] = sound
