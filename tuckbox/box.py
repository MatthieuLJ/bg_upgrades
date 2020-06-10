import math
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image


RESOLUTION = 600  # Dots Per Inch
POINT_PER_MM = RESOLUTION / 24.5  # 24.5 mm per inch

class TuckBoxDrawing:
    def __init__(self, tuckbox, paper, faces, options):
        self.tuckbox = tuckbox
        self.paper = paper
        self.faces = faces
        self.options = options

    def lip_size(self):
        # the lip is the minimum of
        # 80% of the depth
        # 80% of the width
        return min(self.tuckbox['depth'], .3 * self.tuckbox['width'])


    def pattern_height(self):
        return self.tuckbox['height'] + (2 * self.tuckbox['depth']) + self.lip_size()


    def pattern_width(self):
        return (3*self.tuckbox['depth']) + (2*self.tuckbox['width'])


    def draw_box(self):

        draw = Drawing()

        draw.scale(POINT_PER_MM, POINT_PER_MM)

        draw.stroke_width = 1 / POINT_PER_MM

        # Find the coordinate of the left top corner to start drawing from there
        margin_height = 1+(self.paper['height'] - self.pattern_height()) / 2
        margin_width = 1+(self.paper['width'] - self.pattern_width()) / 2

        draw.translate(margin_width,
                    margin_height + self.lip_size() + self.tuckbox['depth'])

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

        tab_length = min(.9 * self.tuckbox['depth'], .4 * self.tuckbox['width'])
        dash_array = [min(self.tuckbox['depth'], self.tuckbox['width'],
                        self.tuckbox['height'])/6.5] * 2

        # Draw the solid lines
        draw.polyline([(self.tuckbox['depth'] + self.tuckbox['width']*.2, -self.tuckbox['depth']),
                    (self.tuckbox['depth'], -self.tuckbox['depth']),
                    (self.tuckbox['depth'], 0),
                    (self.tuckbox['depth']*.9, -tab_length),
                    (self.tuckbox['depth']*.1, -tab_length),
                    (0, 0),
                    (0, self.tuckbox['height']),
                    (self.tuckbox['depth']*.1, self.tuckbox['height'] + tab_length),
                    (self.tuckbox['depth']*.9, self.tuckbox['height'] + tab_length),
                    (self.tuckbox['depth'], self.tuckbox['height']),
                    (self.tuckbox['depth'], self.tuckbox['height'] + self.tuckbox['depth']),
                    (self.tuckbox['depth'] + self.tuckbox['width'],
                        self.tuckbox['height'] + self.tuckbox['depth']),
                    (self.tuckbox['depth'] + self.tuckbox['width'], self.tuckbox['height']),
                    (self.tuckbox['depth']*1.1 + self.tuckbox['width'],
                        self.tuckbox['height'] + tab_length),
                    (self.tuckbox['depth']*1.9 + self.tuckbox['width'],
                        self.tuckbox['height'] + tab_length),
                    (self.tuckbox['depth']*2 + self.tuckbox['width'], self.tuckbox['height']),
                    (self.tuckbox['depth']*2 + self.tuckbox['width'],
                        self.tuckbox['height'] + self.tuckbox['depth']*.8),
                    (self.tuckbox['depth']*2 + self.tuckbox['width']*2,
                        self.tuckbox['height'] + self.tuckbox['depth']*.8),
                    (self.tuckbox['depth']*2 + self.tuckbox['width']*2, 0),
                    (self.tuckbox['depth']*2 + self.tuckbox['width']*1.6, 0),
                    ])
        draw.polyline([(self.tuckbox['depth']*2 + self.tuckbox['width']*1.4, 0),
                    (self.tuckbox['depth']*2 + self.tuckbox['width'], 0),
                    (self.tuckbox['depth']*1.9 + self.tuckbox['width'], -tab_length),
                    (self.tuckbox['depth']*1.1 + self.tuckbox['width'], -tab_length),
                    (self.tuckbox['depth'] + self.tuckbox['width'], 0),
                    (self.tuckbox['depth'] + self.tuckbox['width'], -self.tuckbox['depth']),
                    (self.tuckbox['depth'] + self.tuckbox['width']*.8, -self.tuckbox['depth']),
                    ])

        # 1/2 left of lip
        draw.bezier([(self.tuckbox['depth'], -self.tuckbox['depth']),
                    (self.tuckbox['depth'], -self.tuckbox['depth'] - .75*self.lip_size()),
                    (self.tuckbox['depth'] + .2 * self.tuckbox['width'],
                    -self.tuckbox['depth'] - self.lip_size()),
                    (self.tuckbox['depth'] + .5 * self.tuckbox['width'],
                    -self.tuckbox['depth'] - self.lip_size())])

        # 1/2 right of lip
        draw.bezier([(self.tuckbox['depth'] + self.tuckbox['width'], -self.tuckbox['depth']),
                    (self.tuckbox['depth'] + self.tuckbox['width'],
                    -self.tuckbox['depth'] - .75*self.lip_size()),
                    (self.tuckbox['depth'] + .8 * self.tuckbox['width'],
                    -self.tuckbox['depth'] - self.lip_size()),
                    (self.tuckbox['depth'] + .5 * self.tuckbox['width'],
                    -self.tuckbox['depth'] - self.lip_size())])

        # finger hold
        finger_draw.fill_color = Color('white')
        finger_draw.fill_opacity = 1
        finger_draw.arc((self.tuckbox['depth']*2 + self.tuckbox['width']*1.4, -self.tuckbox['width']*.1),
                        (self.tuckbox['depth']*2 + self.tuckbox['width']
                        * 1.6, self.tuckbox['width']*.1),
                        (0, 180))

        # dashed lines
        dashed_draw.stroke_color = Color('rgb(200,200,200)')
        dashed_draw.stroke_width = .2 / POINT_PER_MM
        dashed_draw.stroke_dash_array = dash_array
        dashed_draw.line((0, 0), (self.tuckbox['depth']*2 + self.tuckbox['width'], 0))
        dashed_draw.line((self.tuckbox['depth'] + self.tuckbox['width']*.2, -self.tuckbox['depth']),
                (self.tuckbox['depth'] + self.tuckbox['width']*.8, -self.tuckbox['depth']))
        dashed_draw.line((0, self.tuckbox['height']),
                (self.tuckbox['depth']*2 + self.tuckbox['width']*2, self.tuckbox['height']))
        dashed_draw.line((self.tuckbox['depth'], 0),
                (self.tuckbox['depth'], self.tuckbox['height']))
        dashed_draw.line((self.tuckbox['depth'] + self.tuckbox['width'], 0),
                (self.tuckbox['depth'] + self.tuckbox['width'], self.tuckbox['height']))
        dashed_draw.line((self.tuckbox['depth']*2 + self.tuckbox['width'], 0),
                (self.tuckbox['depth']*2 + self.tuckbox['width'], self.tuckbox['height']))

        # Create the image
        image = Image(width=math.ceil(self.paper['width'] * POINT_PER_MM),
                    height=math.ceil(self.paper['height'] * POINT_PER_MM))
        image.resolution = RESOLUTION
        image.unit = 'pixelsperinch'

        # Put the pictures in first
        face_sizes = {
            "front": (math.ceil(self.tuckbox['width'] * POINT_PER_MM),
                    math.ceil(self.tuckbox['height'] * POINT_PER_MM)),
            "back": (math.ceil(self.tuckbox['width'] * POINT_PER_MM),
                    math.ceil(self.tuckbox['height'] * POINT_PER_MM)),
            "left": (math.ceil(self.tuckbox['depth'] * POINT_PER_MM),
                    math.ceil(self.tuckbox['height'] * POINT_PER_MM)),
            "right": (math.ceil(self.tuckbox['depth'] * POINT_PER_MM),
                    math.ceil(self.tuckbox['height'] * POINT_PER_MM)),
            "top": (math.ceil(self.tuckbox['width'] * POINT_PER_MM),
                    math.ceil(self.tuckbox['depth'] * POINT_PER_MM)),
            "bottom": (math.ceil(self.tuckbox['width'] * POINT_PER_MM),
                    math.ceil(self.tuckbox['depth'] * POINT_PER_MM)),
        }
        face_positions = {
            "front": (math.floor((margin_width + self.tuckbox['depth']) * POINT_PER_MM),
                    math.floor((margin_height + self.lip_size() + self.tuckbox['depth']) * POINT_PER_MM)),
            "back": (math.floor((margin_width + self.tuckbox['depth']*2 + self.tuckbox['width']) * POINT_PER_MM),
                    math.floor((margin_height + self.lip_size() + self.tuckbox['depth']) * POINT_PER_MM)),
            "left": (math.floor(margin_width * POINT_PER_MM),
                    math.floor((margin_height + self.lip_size() + self.tuckbox['depth']) * POINT_PER_MM)),
            "right": (math.floor((margin_width + self.tuckbox['depth'] + self.tuckbox['width']) * POINT_PER_MM),
                    math.floor((margin_height + self.lip_size() + self.tuckbox['depth']) * POINT_PER_MM)),
            "top": (math.floor((margin_width + self.tuckbox['depth']) * POINT_PER_MM),
                    math.floor((margin_height + self.lip_size()) * POINT_PER_MM)),
            "bottom": (math.floor((margin_width + self.tuckbox['depth']) * POINT_PER_MM),
                    math.floor((margin_height + self.lip_size() + self.tuckbox['depth'] + self.tuckbox['height']) * POINT_PER_MM)),
        }
        face_angles = {
            "front": self.options['front_angle'] if 'front_angle' in self.options else 0,
            "back": self.options['back_angle'] if 'back_angle' in self.options else 0,
            "left": self.options['left_angle'] if 'left_angle' in self.options else 0,
            "right": self.options['right_angle'] if 'right_angle' in self.options else 0,
            "top": self.options['top_angle'] if 'top_angle' in self.options else 0,
            "bottom": self.options['bottom_angle'] if 'bottom_angle' in self.options else 0,
        }
        for side in ["front", "back", "left", "right", "top", "bottom"]:
            if side in self.faces:
                with Image(file=self.faces[side]) as i:
                    i.rotate(face_angles[side] * 90)
                    i.resize(*face_sizes[side])
                    image.composite(i, *face_positions[side])

        draw.draw(image)
        finger_draw.draw(image)
        dashed_draw.draw(image)

        return image


    def create_box_file(self, filename):
        image = self.draw_box()

        image.save(filename=filename)


if __name__ == "__main__":
    with open("front.jpg", "rb") as front, open("back.jpg", "rb") as back, open("left.jpg", "rb") as left, open("right.jpg", "rb") as right, open("top.jpg", "rb") as top, open("bottom.jpg", "rb") as bottom:
        faces = {'front': front, 'back': back, 'left': left,
                 'right': right, 'top': top, 'bottom': bottom}
        paper = {'width': 200, 'height': 200}
        tuckbox = {'height': 50, 'width': 40, 'depth': 20}
        options = {'left_angle':3, 'right_angle':1, 'bottom_angle':2}
        box = TuckBoxDrawing(tuckbox, paper, faces, options)
        box.create_box_file("example.pdf")
