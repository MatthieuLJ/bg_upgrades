import math
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


RESOLUTION = 300  # Dots Per Inch
POINT_PER_MM = RESOLUTION / 24.5  # 24.5 mm per inch


def lip_size(tuckbox):
    # the lip is the minimum of
    # 80% of the depth
    # 80% of the width
    return min(tuckbox['depth'], .3 * tuckbox['width'])


def pattern_height(tuckbox):
    return tuckbox['height'] + (2 * tuckbox['depth']) + lip_size(tuckbox)


def pattern_width(tuckbox):
    return (3*tuckbox['depth']) + (2*tuckbox['width'])


def draw_box(paper, tuckbox, faces):
    image = Image(width=math.ceil(paper['width'] * POINT_PER_MM),
                  height=math.ceil(paper['height'] * POINT_PER_MM))

    image.resolution = RESOLUTION
    image.unit = 'pixelsperinch'

    draw = Drawing()

    # test - fill the page in blue
    #draw.fill_color = Color('blue')
    #draw.fill_opacity = 1
    #draw.color(10, 10, 'floodfill')

    draw.fill_color = Color('white')
    draw.fill_opacity = 0
    draw.stroke_color = Color('black')

    draw.scale(POINT_PER_MM, POINT_PER_MM)

    draw.stroke_width = 1 / POINT_PER_MM

    # Find the coordinate of the left top corner to start drawing from there
    margin_height = (paper['height'] - pattern_height(tuckbox)) / 2
    margin_width = (paper['width'] - pattern_width(tuckbox)) / 2

    draw.translate(margin_width,
                   margin_height + lip_size(tuckbox) + tuckbox['depth'])

    #        ---------
    #       /         \
    #      +--- - - ---+
    #  +---+           +---+
    #  |   |           |   |
    #  0- - - - - - - - - -+----+ +----+
    #  |   |           |   |    +-+    |
    #  |                               |
    #  |   |           |   |           |
    #  |                               |
    #  |   |           |   |           |
    #  |                               |
    #  |   |           |   |           |
    #  |                               |
    #  |   |           |   |           |
    #  +- - - - - - - - - - - - - - - -+
    #  |   |           |   |           |
    #  +---+           +---------------+
    #      +-----------+
    #
    # 0 is the origin
    #        ---------
    #       /         \
    #      +---     ---+
    #  +---+ A       G +---+
    #  | A |           |F  |
    #  0                   +----+ +----+
    #  |                      F +-+ E  |
    #  |                               |
    #  |                               |
    #  |                               |
    #  | A                             |
    #  |                             E |
    #  |                               |
    #  |                               |
    #  |                               |
    #  +                               +
    #  | A |          A|  D| E         |
    #  +---+  A        +---+-----------+
    #      +-----------+
    #

    tab_length = min(.9 * tuckbox['depth'], .4 * tuckbox['width'])
    dash_array = [min(tuckbox['depth'], tuckbox['width'],
                      tuckbox['height'])/6.5] * 2

    # Draw the solid lines
    draw.polyline([(tuckbox['depth'] + tuckbox['width']*.2, -tuckbox['depth']),
                   (tuckbox['depth'], -tuckbox['depth']),
                   (tuckbox['depth'], 0),
                   (tuckbox['depth']*.9, -tab_length),
                   (tuckbox['depth']*.1, -tab_length),
                   (0, 0),
                   (0, tuckbox['height']),
                   (tuckbox['depth']*.1, tuckbox['height'] + tab_length),
                   (tuckbox['depth']*.9, tuckbox['height'] + tab_length),
                   (tuckbox['depth'], tuckbox['height']),
                   (tuckbox['depth'], tuckbox['height'] + tuckbox['depth']),
                   (tuckbox['depth'] + tuckbox['width'],
                    tuckbox['height'] + tuckbox['depth']),
                   (tuckbox['depth'] + tuckbox['width'], tuckbox['height']),
                   (tuckbox['depth']*1.1 + tuckbox['width'],
                    tuckbox['height'] + tab_length),
                   (tuckbox['depth']*1.9 + tuckbox['width'],
                    tuckbox['height'] + tab_length),
                   (tuckbox['depth']*2 + tuckbox['width'], tuckbox['height']),
                   (tuckbox['depth']*2 + tuckbox['width'],
                    tuckbox['height'] + tuckbox['depth']*.8),
                   (tuckbox['depth']*2 + tuckbox['width']*2,
                    tuckbox['height'] + tuckbox['depth']*.8),
                   (tuckbox['depth']*2 + tuckbox['width']*2, 0),
                   (tuckbox['depth']*2 + tuckbox['width']*1.6, 0),
                   ])
    draw.polyline([(tuckbox['depth']*2 + tuckbox['width']*1.4, 0),
                   (tuckbox['depth']*2 + tuckbox['width'], 0),
                   (tuckbox['depth']*1.9 + tuckbox['width'], -tab_length),
                   (tuckbox['depth']*1.1 + tuckbox['width'], -tab_length),
                   (tuckbox['depth'] + tuckbox['width'], 0),
                   (tuckbox['depth'] + tuckbox['width'], -tuckbox['depth']),
                   (tuckbox['depth'] + tuckbox['width']*.8, -tuckbox['depth']),
                   ])

    # 1/2 left of lip
    draw.bezier([(tuckbox['depth'], -tuckbox['depth']),
                 (tuckbox['depth'], -tuckbox['depth'] - .75*lip_size(tuckbox)),
                 (tuckbox['depth'] + .2 * tuckbox['width'],
                  -tuckbox['depth'] - lip_size(tuckbox)),
                 (tuckbox['depth'] + .5 * tuckbox['width'],
                  -tuckbox['depth'] - lip_size(tuckbox))])

    # 1/2 right of lip
    draw.bezier([(tuckbox['depth'] + tuckbox['width'], -tuckbox['depth']),
                 (tuckbox['depth'] + tuckbox['width'],
                  -tuckbox['depth'] - .75*lip_size(tuckbox)),
                 (tuckbox['depth'] + .8 * tuckbox['width'],
                  -tuckbox['depth'] - lip_size(tuckbox)),
                 (tuckbox['depth'] + .5 * tuckbox['width'],
                  -tuckbox['depth'] - lip_size(tuckbox))])

    # finger hold
    draw.arc((tuckbox['depth']*2 + tuckbox['width']*1.4, -tuckbox['width']*.1),
             (tuckbox['depth']*2 + tuckbox['width']*1.6, tuckbox['width']*.1),
             (0, 180))

    # dashed lines
    draw.stroke_color = Color('rgb(200,200,200)')
    draw.stroke_width = .2 / POINT_PER_MM
    draw.stroke_dash_array = dash_array
    draw.line((0, 0), (tuckbox['depth']*2 + tuckbox['width'], 0))
    draw.line((tuckbox['depth'] + tuckbox['width']*.2, -tuckbox['depth']),
              (tuckbox['depth'] + tuckbox['width']*.8, -tuckbox['depth']))
    draw.line((0, tuckbox['height']),
              (tuckbox['depth']*2 + tuckbox['width']*2, tuckbox['height']))
    draw.line((tuckbox['depth'], 0),
              (tuckbox['depth'], tuckbox['height']))
    draw.line((tuckbox['depth'] + tuckbox['width'], 0),
              (tuckbox['depth'] + tuckbox['width'], tuckbox['height']))
    draw.line((tuckbox['depth']*2 + tuckbox['width'], 0),
              (tuckbox['depth']*2 + tuckbox['width'], tuckbox['height']))

    draw(image)

    return image


def create_box_file(filename, paper, tuckbox, faces):
    image = draw_box(paper, tuckbox, faces)

    image.save(filename=filename)


if __name__ == "__main__":
    paper = {'width': 200, 'height': 200}
    tuckbox = {'height': 50, 'width': 40, 'depth': 20}
    create_box_file("example.pdf", paper, tuckbox, {})
