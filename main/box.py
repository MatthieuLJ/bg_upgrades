# for all functions taking tuckbox, this is a dictionary with
# height, width, depth

import math
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


RESOLUTION = 300  # Dots Per Inch
POINT_PER_MM = RESOLUTION / 24.5 # 24.5 mm per inch

def lip_size(tuckbox):
    # the lip is the minimum of
    # 80% of the depth
    # 80% of the width
    return .8 * min(tuckbox['depth'], tuckbox['width'])

def pattern_height(tuckbox):
    return tuckbox['height'] + ( 2* tuckbox['depth'] ) + lip_size(tuckbox)

def pattern_width(tuckbox):
    return ( 3*tuckbox['depth'] ) + ( 2*tuckbox['width'])

def draw_box(paper, tuckbox):
    image = Image(width = math.ceil(paper['width'] * POINT_PER_MM),
            height = math.ceil(paper['height'] * POINT_PER_MM))

    image.resolution = RESOLUTION
    image.unit = 'pixelsperinch'

    draw = Drawing()

    # test - fill the page in blue
    draw.fill_color = Color('blue')
    draw.fill_opacity = 1
    draw.color(10,10, 'floodfill')


    draw.fill_color = Color('white')
    draw.fill_opacity = 1
    draw.stroke_color = Color('black')
    
    draw.scale(POINT_PER_MM, POINT_PER_MM)

    draw.stroke_width = 1 / POINT_PER_MM

    # Find the coordinate of the left top corner to start drawing from there
    margin_height = (paper['height'] - pattern_height(tuckbox)) / 2
    margin_width = (paper['width'] - pattern_width(tuckbox)) / 2

    draw.translate(margin_width,
            margin_height + lip_size(tuckbox) + tuckbox['depth'])

    # left side
    draw.rectangle(left = 0, top = 0, 
            width = tuckbox['depth'] , height = tuckbox['height'])
    draw(image)

    # back
    draw.rectangle(left = tuckbox['depth'], top = 0,
            width = tuckbox['width'], height = tuckbox['height'])
    draw(image)

    # right side
    draw.rectangle(left = tuckbox['depth'] + tuckbox['width'], top = 0,
            width = tuckbox['depth'], height = tuckbox['height'])
    draw(image)

    # front
    draw.rectangle(left = 2 * tuckbox['depth'] + tuckbox['width'], top = 0,
            width = tuckbox['width'], height = tuckbox['height'])
    draw(image)

    # top
    draw.rectangle(left = tuckbox['depth'], top = - tuckbox['depth'],
            width = tuckbox['width'], height = tuckbox['depth'])
    draw(image)

    # 1/2 left of lip
    points = [(tuckbox['depth'], -tuckbox['depth']),
            (tuckbox['depth'], -tuckbox['depth'] - .75*lip_size(tuckbox)),
            (tuckbox['depth'] + .2 * tuckbox['width'],
                -tuckbox['depth'] - lip_size(tuckbox)),
            (tuckbox['depth'] + .5 * tuckbox['width'],
                -tuckbox['depth'] - lip_size(tuckbox))]
    draw.bezier(points)
    draw(image)

    # 1/2 right of lip
    points = [(tuckbox['depth'] + tuckbox['width'], -tuckbox['depth']),
            (tuckbox['depth'] + tuckbox['width'],
                -tuckbox['depth'] - .75*lip_size(tuckbox)),
            (tuckbox['depth'] + .8 * tuckbox['width'],
                -tuckbox['depth'] - lip_size(tuckbox)),
            (tuckbox['depth'] + .5 * tuckbox['width'],
                -tuckbox['depth'] - lip_size(tuckbox))]
    draw.bezier(points)
    draw(image)

    image.save(filename="example.pdf")


if __name__ == "__main__":
    paper = { 'width': 200, 'height': 200 }
    tuckbox = { 'height': 50, 'width': 40, 'depth': 20 }
    draw_box(paper, tuckbox)


