# for all functions taking tuckbox, this is a dictionary with
# height, width, depth

import math
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


POINT_PER_MM = 72/25.4

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

    draw = Drawing()
    draw.fill_color = Color('white')
    draw.stroke_color = Color('black')
    draw.stroke_width = 1
    
    draw.scale(POINT_PER_MM, POINT_PER_MM)

    # Find the coordinate of the left top corner to start drawing from there
    margin_height = (paper['height'] - pattern_height(tuckbox)) / 2
    margin_width = (paper['width'] - pattern_width(tuckbox)) / 2

    draw.translate(margin_width,
            margin_height + lip_size(tuckbox) + tuckbox['depth'])

    draw.rectangle(left = 0, top = 0, 
            width = tuckbox['depth'] , height = tuckbox['height'])
    draw(image)

    draw.rectangle(left = tuckbox['depth'], top = 0,
            width = tuckbox['width'], height = tuckbox['height'])
    draw(image)

    draw.rectangle(left = tuckbox['depth'] + tuckbox['width'], top = 0,
            width = tuckbox['depth'], height = tuckbox['height'])
    draw(image)

    image.save(filename="example.png")


if __name__ == "__main__":
    paper = { 'width': 200, 'height': 200 }
    tuckbox = { 'height': 50, 'width': 40, 'depth': 20 }
    draw_box(paper, tuckbox)


