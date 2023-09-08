import mock
import pygame

import pythonGraph


def _get_window_title():
    title, icontitle = pygame.display.get_caption()
    return title


def setup_function(function):
    set_mode = pygame.display.set_mode

    def mock_set_mode(size):
        # enable transparency (https://stackoverflow.com/questions/14948711/)
        return set_mode(size, flags=0, depth=32)

    with mock.patch('pygame.mixer.init') as mock_mixer_init, \
            mock.patch('pygame.display.set_mode',
                       wraps=mock_set_mode) as mock_display_set_mode:
        pythonGraph.open_window(400, 300)

        mock_mixer_init.assert_called_once_with()
        mock_display_set_mode.assert_called_once()


def teardown_function(function):
    pythonGraph.close_window()


def test_open_window():
    assert pygame.display.get_surface() is not None
    assert 'pythonGraph' == _get_window_title()


def test_set_window_title():
    pythonGraph.set_window_title('fake-title')
    assert 'fake-title' == _get_window_title()


def test_close_window():
    assert pygame.display.get_surface() is not None

    pythonGraph.close_window()
    assert pygame.display.get_surface() is None


def test_window_closed():
    assert not pythonGraph.window_closed()

    pythonGraph.close_window()
    assert pythonGraph.window_closed()


def test_window_not_closed():
    assert pythonGraph.window_not_closed()

    pythonGraph.close_window()
    assert not pythonGraph.window_not_closed()


@mock.patch('random.randint')
def test_create_random_color(mock_random):
    pythonGraph.create_random_color()
    mock_random.assert_has_calls([
        mock.call(0, 255),
        mock.call(0, 255),
        mock.call(0, 255),
    ])


def test__get_rectangle():
    rectangle = pythonGraph.pythonGraph._get_rectangle(100, 100, 200, 200)
    assert rectangle.topleft == (100, 100)
    assert rectangle.topright == (201, 100)
    assert rectangle.bottomleft == (100, 201)
    assert rectangle.bottomright == (201, 201)

    rectangle = pythonGraph.pythonGraph._get_rectangle(200, 200, 100, 100)
    assert rectangle.topleft == (100, 100)
    assert rectangle.topright == (201, 100)
    assert rectangle.bottomleft == (100, 201)
    assert rectangle.bottomright == (201, 201)


def test_clear_window():
    pythonGraph.clear_window("black")
    assert pygame.Color("black") == pythonGraph.get_color(200, 150)

    pythonGraph.clear_window("red")
    assert pygame.Color("red") == pythonGraph.get_color(200, 150)


def test_draw_arc():
    pythonGraph.draw_arc(100, 100, 199, 199, 150, 199, 199, 150, "red")

    radius = int(round(50 / 2**0.5))
    assert pygame.Color("red") == pythonGraph.get_color(150, 199)
    assert pygame.Color("red") == pythonGraph.get_color(199, 150 + 1)
    assert pygame.Color("red") == pythonGraph.get_color(150 + radius - 1,
                                                        150 + radius)

    assert pygame.Color("white") == pythonGraph.get_color(150 - radius - 1,
                                                          150 + radius)
    assert pygame.Color("white") == pythonGraph.get_color(150 + radius - 1,
                                                          150 - radius)
    assert pygame.Color("white") == pythonGraph.get_color(150 - radius - 1,
                                                          150 - radius)

    pythonGraph.draw_arc(100, 100, 199, 199, 150, 199, 150, 100, "red")

    radius = int(round(50 / 2**0.5))
    assert pygame.Color("red") == pythonGraph.get_color(150, 199)
    assert pygame.Color("red") == pythonGraph.get_color(150 + 2, 100)
    assert pygame.Color("red") == pythonGraph.get_color(199, 150)
    assert pygame.Color("red") == pythonGraph.get_color(150 + radius - 1,
                                                        150 + radius)
    assert pygame.Color("red") == pythonGraph.get_color(150 + radius - 1,
                                                        150 - radius)

    assert pygame.Color("white") == pythonGraph.get_color(150 - radius - 1,
                                                          150 + radius)
    assert pygame.Color("white") == pythonGraph.get_color(150 - radius - 1,
                                                          150 - radius)


def _test_draw_circle(filled):
    pythonGraph.draw_circle(200, 150, 50, "red", filled)

    # NOTE: The following coordinates are wonky -- not the same as an ellipse
    # that is centered inside the same bounding box. Not sure exactly what's
    # going on here...possibly an off-by-one error in how the coordinates are
    # interpreted for the shapes.
    for x in [151, 249]:
        assert pygame.Color("red") == pythonGraph.get_color(x, 150)
    for y in [101, 199]:
        assert pygame.Color("red") == pythonGraph.get_color(200, y)

    # point outside the circle
    assert pygame.Color("white") == pythonGraph.get_color(255, 155)


def test_draw_cirlce_filled():
    _test_draw_circle(True)

    # point inside the circle
    assert pygame.Color("red") == pythonGraph.get_color(200, 150)


def test_draw_cirlce_not_filled():
    _test_draw_circle(False)

    # point inside the circle
    assert pygame.Color("white") == pythonGraph.get_color(200, 150)


def _test_draw_ellipse(filled):
    pythonGraph.draw_ellipse(150, 100, 250, 200, "red", filled)

    # NOTE: The following coordinates are wonky -- not the same as a circle
    # that is centered inside the same bounding box. Not sure exactly what's
    # going on here...possibly an off-by-one error in how the coordinates are
    # interpreted for the shapes.
    for x in [150, 250]:
        assert pygame.Color("red") == pythonGraph.get_color(x, 150)
    for y in [100, 200]:
        assert pygame.Color("red") == pythonGraph.get_color(200, y)

    # point outside the ellipse
    assert pygame.Color("white") == pythonGraph.get_color(255, 155)


def test_draw_ellipse_filled():
    _test_draw_ellipse(True)

    # point inside the ellipse
    assert pygame.Color("red") == pythonGraph.get_color(200, 150)


def test_draw_ellipse_not_filled():
    _test_draw_ellipse(False)

    # point inside the ellipse
    assert pygame.Color("white") == pythonGraph.get_color(200, 150)


def test_draw_image():
    pythonGraph.draw_image('pythonGraph/examples/media/test.png',
                           0, 0, 300, 300)

    assert pygame.Color("white") == pythonGraph.get_color(1, 1)
    assert pygame.Color("white") == pythonGraph.get_color(100, 100)
    assert pygame.Color("white") == pythonGraph.get_color(200, 200)

    assert pythonGraph.create_color(215, 11, 11) == \
        pythonGraph.get_color(35, 35)
    assert pythonGraph.create_color(51, 11, 215) == \
        pythonGraph.get_color(60, 60)
    assert pythonGraph.create_color(255, 242, 20) == \
        pythonGraph.get_color(170, 125)
    assert pythonGraph.create_color(52, 157, 20) == \
        pythonGraph.get_color(110, 200)


@mock.patch('pythonGraph.pythonGraph.win')
def test_draw_image_centered(mock_win):
    pythonGraph.draw_image('pythonGraph/examples/media/test.png',
                           0, 0, 300, 300, centered=True)
    mock_win.blit.assert_called_once_with(mock.ANY, (-150, -150))


@mock.patch('pythonGraph.pythonGraph.win')
def test_draw_image_rotate(mock_win):
    for degrees in [45, 90, 180]:
        with mock.patch('pygame.transform.rotate') as mock_rotate:
            pythonGraph.draw_image('pythonGraph/examples/media/test.png',
                                   0, 0, 300, 300, rotation=degrees)
            mock_rotate.assert_called_once_with(mock.ANY, -degrees)


def test_draw_image_transparent():
    pythonGraph.clear_window('black')
    pythonGraph.draw_image('pythonGraph/examples/media/test.png',
                           0, 0, 300, 300)

    assert pygame.Color("black") == pythonGraph.get_color(1, 1)
    assert pygame.Color("black") == pythonGraph.get_color(100, 100)
    assert pygame.Color("black") == pythonGraph.get_color(200, 200)

    assert pythonGraph.create_color(215, 11, 11) == \
        pythonGraph.get_color(35, 35)
    assert pythonGraph.create_color(52, 157, 20) == \
        pythonGraph.get_color(110, 200)
    assert pythonGraph.create_color(255, 242, 20) == \
        pythonGraph.get_color(170, 125)
    assert pythonGraph.create_color(52, 157, 20) == \
        pythonGraph.get_color(110, 200)


def test_draw_line():
    pythonGraph.draw_line(150, 150, 250, 150, "red")

    assert pygame.Color("red") == pythonGraph.get_color(150, 150)
    assert pygame.Color("red") == pythonGraph.get_color(250, 150)

    assert pygame.Color("red") == pythonGraph.get_color(200, 150)

    assert pygame.Color("white") == pythonGraph.get_color(149, 150)
    assert pygame.Color("white") == pythonGraph.get_color(251, 150)


def test_draw_pixel():
    pythonGraph.draw_pixel(2, 2, "red")

    assert pygame.Color("red") == pythonGraph.get_color(2, 2)

    assert pygame.Color("white") == pythonGraph.get_color(1, 1)
    assert pygame.Color("white") == pythonGraph.get_color(3, 3)


def test_draw_rectangle_filled():
    pythonGraph.draw_rectangle(150, 150, 250, 200, "red", True)

    # points inside recntangle
    assert pygame.Color("red") == pythonGraph.get_color(150, 150)
    assert pygame.Color("red") == pythonGraph.get_color(250, 150)
    assert pygame.Color("red") == pythonGraph.get_color(150, 200)
    assert pygame.Color("red") == pythonGraph.get_color(250, 200)
    assert pygame.Color("red") == pythonGraph.get_color(200, 175)

    # points outside rectangle
    assert pygame.Color("white") == pythonGraph.get_color(149, 149)
    assert pygame.Color("white") == pythonGraph.get_color(251, 201)


def test_draw_rectangle_not_filled():
    pythonGraph.draw_rectangle(150, 150, 250, 200, "red", False)

    # points on recntangle's circumference
    assert pygame.Color("red") == pythonGraph.get_color(150, 150)
    assert pygame.Color("red") == pythonGraph.get_color(250, 150)
    assert pygame.Color("red") == pythonGraph.get_color(150, 200)
    assert pygame.Color("red") == pythonGraph.get_color(250, 200)

    # point inside rectangle
    assert pygame.Color("white") == pythonGraph.get_color(200, 175)

    # points outside rectangle
    assert pygame.Color("white") == pythonGraph.get_color(149, 149)
    assert pygame.Color("white") == pythonGraph.get_color(251, 201)


def test_draw_text():
    # FIXME: Reuse same test case as write_text
    #   Not sure what's happening here: When invoking the same code as
    # test_write_text, Python crashes on macOS Mojave (10.14.6) with Python
    # 2.7.17, but each test case executes okay in isolation (i.e., when the
    # other is removed).
    """
    pythonGraph.draw_text('Hello, World!', 1, 1, "black", 64)

    assert pygame.Color("black") == pythonGraph.get_color(5, 5)

    assert pygame.Color("white") == pythonGraph.get_color(1, 1)
    assert pygame.Color("white") == pythonGraph.get_color(100, 100)
    """
    with mock.patch('pythonGraph.pythonGraph.write_text') as mock_write_text:
        pythonGraph.draw_text('Hello, World!', 1, 1, 'black', 64)

        mock_write_text.assert_called_once_with('Hello, World!', 1, 1,
                                                'black', 64)

    # background
    with mock.patch('pythonGraph.pythonGraph.draw_rectangle') as \
            mock_draw_rectangle, \
         mock.patch('pythonGraph.pythonGraph.write_text') as mock_write_text:
        pythonGraph.draw_text('Hello, World!', 1, 1, 'black', 64,
                              background='white')

        mock_draw_rectangle.assert_called_once_with(1, 1, mock.ANY, mock.ANY,
                                                    'white', True)
        mock_write_text.assert_called_once_with('Hello, World!', 1, 1,
                                                'black', 64)

    # border
    with mock.patch('pythonGraph.pythonGraph.draw_rectangle') as \
            mock_draw_rectangle, \
         mock.patch('pythonGraph.pythonGraph.write_text') as mock_write_text:
        pythonGraph.draw_text('Hello, World!', 1, 1, 'black', 64,
                              border='white')

        mock_draw_rectangle.assert_called_once_with(0, 0, mock.ANY, mock.ANY,
                                                    'white', False, width=1)
        mock_write_text.assert_called_once_with('Hello, World!', 1, 1,
                                                'black', 64)

    # border_width (with border)
    with mock.patch('pythonGraph.pythonGraph.draw_rectangle') as \
            mock_draw_rectangle, \
         mock.patch('pythonGraph.pythonGraph.write_text') as mock_write_text:
        pythonGraph.draw_text('Hello, World!', 10, 10, 'black', 64,
                              border='white', border_width=5)

        mock_draw_rectangle.assert_called_once_with(5, 5, mock.ANY, mock.ANY,
                                                    'white', False, width=5)
        mock_write_text.assert_called_once_with('Hello, World!', 10, 10,
                                                'black', 64)

    # centered
    with mock.patch('pythonGraph.pythonGraph.write_text') as mock_write_text:
        pythonGraph.draw_text('Hello, World!', 200, 200, 'black', 64,
                              centered=True)

        mock_write_text.assert_called_once_with('Hello, World!',
                                                mock.ANY, mock.ANY,
                                                'black', 64)

        x, y = mock_write_text.call_args.args[1:3]
        # centering should shift x and y coordinates, but the amount may vary
        assert x < 200 and y < 200, \
            "Text does not appear to be centered on coordinates (200, 200)"

    # padding
    with mock.patch('pythonGraph.pythonGraph.draw_rectangle') as \
            mock_draw_rectangle, \
         mock.patch('pythonGraph.pythonGraph.write_text') as mock_write_text:
        pythonGraph.draw_text('Hello, World!', 10, 10, 'black', 64,
                              background='white', padding=5)

        mock_draw_rectangle.assert_called_once_with(5, 5, mock.ANY, mock.ANY,
                                                    'white', True)
        mock_write_text.assert_called_once_with('Hello, World!', 10, 10,
                                                'black', 64)


def test_write_text():
    pythonGraph.write_text('Hello, World!', 1, 1, 'black', 64)

    assert pygame.Color("black") == pythonGraph.get_color(5, 5)

    assert pygame.Color("white") == pythonGraph.get_color(1, 1)
    assert pygame.Color("white") == pythonGraph.get_color(100, 100)


def test_key_pressed():
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)  # down arrow
    with mock.patch('pythonGraph.pythonGraph._get_events') as mock_get_events:
        mock_get_events.return_value = [event]

        assert pythonGraph.key_pressed('down')
        assert pythonGraph.key_pressed('DOWN')

        assert not pythonGraph.key_pressed('up')
        assert not pythonGraph.key_pressed('UP')


def test_key_down():
    for key in ['down', 'DOWN']:
        with mock.patch('pygame.key.key_code') as mock_key_code:
            pythonGraph.key_down(key)
            mock_key_code.assert_called_once_with(key)


def test_key_released():
    event = pygame.event.Event(pygame.KEYUP, key=pygame.K_DOWN)  # down arrow
    with mock.patch('pythonGraph.pythonGraph._get_events') as mock_get_events:
        mock_get_events.return_value = [event]

        assert pythonGraph.key_released('down')
        assert pythonGraph.key_released('DOWN')

        assert not pythonGraph.key_released('up')
        assert not pythonGraph.key_released('UP')


def test_get_window_height():
    assert 300 == pythonGraph.get_window_height()


def test_get_window_width():
    assert 400 == pythonGraph.get_window_width()


@mock.patch('pygame.time.delay')
@mock.patch('pygame.display.update')
@mock.patch('pygame.event.pump')
def test_update_window(mock_pump, mock_update, mock_delay):
    pythonGraph.update_window()

    mock_pump.assert_called_once_with()
    mock_update.assert_called_once_with()
    mock_delay.assert_called_once()
