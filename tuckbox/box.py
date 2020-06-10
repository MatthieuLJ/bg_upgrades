import math
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


RESOLUTION = 600  # Dots Per Inch
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


def draw_box(paper, tuckbox, faces, options):

    draw = Drawing()

    draw.scale(POINT_PER_MM, POINT_PER_MM)

    draw.stroke_width = 1 / POINT_PER_MM

    # Find the coordinate of the left top corner to start drawing from there
    margin_height = 1+(paper['height'] - pattern_height(tuckbox)) / 2
    margin_width = 1+(paper['width'] - pattern_width(tuckbox)) / 2

    draw.translate(margin_width,
                   margin_height + lip_size(tuckbox) + tuckbox['depth'])

    finger_draw = Drawing(draw)
    dashed_draw = Drawing(draw)

    draw.fill_color = Color('white')
    draw.fill_opacity = 0
    draw.stroke_color = Color('black')

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
    finger_draw.fill_color = Color('white')
    finger_draw.fill_opacity = 1
    finger_draw.arc((tuckbox['depth']*2 + tuckbox['width']*1.4, -tuckbox['width']*.1),
                    (tuckbox['depth']*2 + tuckbox['width']
                     * 1.6, tuckbox['width']*.1),
                    (0, 180))

    # dashed lines
    dashed_draw.stroke_color = Color('rgb(200,200,200)')
    dashed_draw.stroke_width = .2 / POINT_PER_MM
    dashed_draw.stroke_dash_array = dash_array
    dashed_draw.line((0, 0), (tuckbox['depth']*2 + tuckbox['width'], 0))
    dashed_draw.line((tuckbox['depth'] + tuckbox['width']*.2, -tuckbox['depth']),
              (tuckbox['depth'] + tuckbox['width']*.8, -tuckbox['depth']))
    dashed_draw.line((0, tuckbox['height']),
              (tuckbox['depth']*2 + tuckbox['width']*2, tuckbox['height']))
    dashed_draw.line((tuckbox['depth'], 0),
              (tuckbox['depth'], tuckbox['height']))
    dashed_draw.line((tuckbox['depth'] + tuckbox['width'], 0),
              (tuckbox['depth'] + tuckbox['width'], tuckbox['height']))
    dashed_draw.line((tuckbox['depth']*2 + tuckbox['width'], 0),
              (tuckbox['depth']*2 + tuckbox['width'], tuckbox['height']))

    # Create the image
    image = Image(width=math.ceil(paper['width'] * POINT_PER_MM),
                  height=math.ceil(paper['height'] * POINT_PER_MM))
    image.resolution = RESOLUTION
    image.unit = 'pixelsperinch'

    # Put the pictures in first
    face_sizes = {
        "front": (math.ceil(tuckbox['width'] * POINT_PER_MM),
                  math.ceil(tuckbox['height'] * POINT_PER_MM)),
        "back": (math.ceil(tuckbox['width'] * POINT_PER_MM),
                 math.ceil(tuckbox['height'] * POINT_PER_MM)),
        "left": (math.ceil(tuckbox['depth'] * POINT_PER_MM),
                 math.ceil(tuckbox['height'] * POINT_PER_MM)),
        "right": (math.ceil(tuckbox['depth'] * POINT_PER_MM),
                  math.ceil(tuckbox['height'] * POINT_PER_MM)),
        "top": (math.ceil(tuckbox['width'] * POINT_PER_MM),
                math.ceil(tuckbox['depth'] * POINT_PER_MM)),
        "bottom": (math.ceil(tuckbox['width'] * POINT_PER_MM),
                   math.ceil(tuckbox['depth'] * POINT_PER_MM)),
    }
    face_positions = {
        "front": (math.floor((margin_width + tuckbox['depth']) * POINT_PER_MM),
                  math.floor((margin_height + lip_size(tuckbox) + tuckbox['depth']) * POINT_PER_MM)),
        "back": (math.floor((margin_width + tuckbox['depth']*2 + tuckbox['width']) * POINT_PER_MM),
                 math.floor((margin_height + lip_size(tuckbox) + tuckbox['depth']) * POINT_PER_MM)),
        "left": (math.floor(margin_width * POINT_PER_MM),
                 math.floor((margin_height + lip_size(tuckbox) + tuckbox['depth']) * POINT_PER_MM)),
        "right": (math.floor((margin_width + tuckbox['depth'] + tuckbox['width']) * POINT_PER_MM),
                  math.floor((margin_height + lip_size(tuckbox) + tuckbox['depth']) * POINT_PER_MM)),
        "top": (math.floor((margin_width + tuckbox['depth']) * POINT_PER_MM),
                math.floor((margin_height + lip_size(tuckbox)) * POINT_PER_MM)),
        "bottom": (math.floor((margin_width + tuckbox['depth']) * POINT_PER_MM),
                   math.floor((margin_height + lip_size(tuckbox) + tuckbox['depth'] + tuckbox['height']) * POINT_PER_MM)),
    }
    face_angles = {
        "front": options['front_angle'] if 'front_angle' in options else 0,
        "back": options['back_angle'] if 'back_angle' in options else 0,
        "left": options['left_angle'] if 'left_angle' in options else 0,
        "right": options['right_angle'] if 'right_angle' in options else 0,
        "top": options['top_angle'] if 'top_angle' in options else 0,
        "bottom": options['bottom_angle'] if 'bottom_angle' in options else 0,
    }
    for side in ["front", "back", "left", "right", "top", "bottom"]:
        if side in faces:
            with Image(file=faces[side]) as i:
                i.rotate(face_angles[side] * 90)
                i.resize(*face_sizes[side])
                image.composite(i, *face_positions[side])

    draw.draw(image)
    finger_draw.draw(image)
    dashed_draw.draw(image)

    return image


def create_box_file(filename, paper, tuckbox, faces, options):
    image = draw_box(paper, tuckbox, faces, options)

    image.save(filename=filename)


if __name__ == "__main__":
    with open("front.jpg", "rb") as front, open("back.jpg", "rb") as back, open("left.jpg", "rb") as left, open("right.jpg", "rb") as right, open("top.jpg", "rb") as top, open("bottom.jpg", "rb") as bottom:
        faces = {'front': front, 'back': back, 'left': left,
                 'right': right, 'top': top, 'bottom': bottom}
        paper = {'width': 200, 'height': 200}
        tuckbox = {'height': 50, 'width': 40, 'depth': 20}
        options = {'left_angle':3, 'right_angle':1, 'bottom_angle':2}
        create_box_file("example.pdf", paper, tuckbox, faces, options)
