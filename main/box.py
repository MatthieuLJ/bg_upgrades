# for all functions taking tuckbox, this is a dictionary with
# height, width, depth

import cairo
import math

from PIL import Image

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
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
            math.ceil(paper['width'] * POINT_PER_MM),
            math.ceil(paper['height'] * POINT_PER_MM))
    ctx = cairo.Context(surface)
    
    ctx.scale(POINT_PER_MM, POINT_PER_MM)

    # Find the coordinate of the left top corner to start drawing from there
    margin_height = (paper['height'] - pattern_height(tuckbox)) / 2
    margin_width = (paper['width'] - pattern_width(tuckbox)) / 2

    ctx.translate(margin_width,
            margin_height + lip_size(tuckbox) + tuckbox['depth'])


    ctx.set_line_width(1 / POINT_PER_MM)

    ctx.set_source_rgb(1,1,1)
    ctx.paint()
    ctx.set_source_rgb(0,0,0)

    ctx.rectangle(0, 0, tuckbox['depth'] , tuckbox['height'])
    ctx.stroke()
    ctx.rectangle(tuckbox['depth'], 0,
            tuckbox['depth'] + tuckbox['width'], tuckbox['height'])
    ctx.stroke()

    surface.write_to_png("example.png")

    return surface

def save_surface_to_pdf(surface, paper):
    pass


if __name__ == "__main__":
    paper = { 'width': 200, 'height': 200 }
    tuckbox = { 'height': 50, 'width': 30, 'depth': 20 }
    surface = draw_box(paper, tuckbox)


