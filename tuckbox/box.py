import math
import os
import stat
import subprocess
import sys
import tempfile
from wand.api import library
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image
from wand.resource import limits


RESOLUTION = 200  # Dots Per Inch
POINT_PER_MM = RESOLUTION / 25.4  # 25.4 mm per inch
WATERMARK = "Tuckbox generated @ https://www.bg-upgrades.net/  -  v1.4 "


class TuckBoxDrawing:
    def __init__(self, tuckbox, paper, faces=None, options=None):
        self.tuckbox = tuckbox
        self.paper = paper
        self.faces = faces if faces is not None else {}
        self.options = options if options is not None else {}

        # Use disk when using more than 100MB of memory
        limits['memory'] = 100 * 1024 * 1024

    def create_box_file(self, filename, progress_tracker=None):
        image = self.draw_box(progress_tracker)

        if image is not None:
            image.save(filename=filename)
            os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

    def lip_size(self):
        # the lip is the minimum of
        # the depth
        # 30% of the width
        return min(self.tuckbox['depth'], .3 * self.tuckbox['width'])

    def pattern_height(self):
        return self.tuckbox['height'] + (2 * self.tuckbox['depth']) + self.lip_size()

    def pattern_width(self):
        return (2.8*self.tuckbox['depth']) + (2*self.tuckbox['width'])

    def will_it_fit(self):
        return ((min(self.pattern_height(), self.pattern_width()) < min(self.paper['height'], self.paper['width'])) and
                (max(self.pattern_height(), self.pattern_width()) < max(self.paper['height'], self.paper['width'])))

    def check_paper_layout(self):
        if not self.will_it_fit():
            return False
        elif self.pattern_height() > self.paper['height'] or self.pattern_width() > self.paper['width']:
            self.paper['width'], self.paper['height'] = self.paper['height'], self.paper['width']
        return True

    def draw_box(self, progress_tracker=None):
        if not self.check_paper_layout():
            return None

        tuckbox_dimensions = ['width', 'height', 'depth']
        paper_dimensions = ['width', 'height']
        if ((not all(dimension in self.tuckbox for dimension in tuckbox_dimensions)) or 
            (not all(dimension in self.paper for dimension in paper_dimensions))):
            return None

        draw = Drawing()

        draw.scale(POINT_PER_MM, POINT_PER_MM)

        draw.stroke_color = Color('black')
        draw.stroke_width = RESOLUTION / (200 * POINT_PER_MM)

        # How much white space on the sides
        margin_height = (self.paper['height'] - self.pattern_height()) / 2
        margin_width = (self.paper['width'] - self.pattern_width()) / 2

        draw.translate(margin_width,
                       margin_height + self.lip_size() + self.tuckbox['depth'])

        finger_draw = Drawing(draw)
        dashed_draw = Drawing(draw)

        draw.fill_opacity = 0

        if progress_tracker is not None:
            progress_tracker(5)

        #        ---------
        #       /         \
        #      +--S - - ---+
        #  +---+           +---+
        #  |   |           |   |
        #  0- - - - - - - - - -+----T +----+--+
        #  |   |           |   |    +-+    |  |
        #  |                                  |
        #  |   |           |   |           |  |
        #  |                                  |
        #  |   |           |   |           |  |
        #  |                                  |
        #  |   |           |   |           |  |
        #  |                                  |
        #  |   |           |   |           |  |
        #  +- - - - - - - - - - - - - - - -+--+
        #  |   |           |   |           |
        #  +---+           +---------------+
        #      +-----------+
        #
        # 0 is the origin
        # S is the start of the first polyline (going counter-clockwise)
        # T is the start of the second one

        tab_length = min(.9 *
                         self.tuckbox['depth'], .4 * self.tuckbox['width'])
        dash_array = [min(self.tuckbox['depth'], self.tuckbox['width'],
                          self.tuckbox['height'])/13] * 2

        # Draw the solid lines
        draw.polyline([(self.tuckbox['depth'] + self.tuckbox['width']*.2, -self.tuckbox['depth']),
                       (self.tuckbox['depth'], -self.tuckbox['depth']),
                       (self.tuckbox['depth'], 0),
                       (self.tuckbox['depth']*.9, -tab_length),
                       (self.tuckbox['depth']*.1, -tab_length),
                       (0, 0),
                       (0, self.tuckbox['height']),
                       (self.tuckbox['depth']*.1,
                        self.tuckbox['height'] + tab_length),
                       (self.tuckbox['depth']*.9,
                        self.tuckbox['height'] + tab_length),
                       (self.tuckbox['depth'], self.tuckbox['height']),
                       (self.tuckbox['depth'],
                        self.tuckbox['height'] + self.tuckbox['depth']),
                       (self.tuckbox['depth'] + self.tuckbox['width'],
                        self.tuckbox['height'] + self.tuckbox['depth']),
                       (self.tuckbox['depth'] + self.tuckbox['width'],
                        self.tuckbox['height']),
                       (self.tuckbox['depth']*1.1 + self.tuckbox['width'],
                        self.tuckbox['height'] + tab_length),
                       (self.tuckbox['depth']*1.9 + self.tuckbox['width'],
                        self.tuckbox['height'] + tab_length),
                       (self.tuckbox['depth']*2 +
                        self.tuckbox['width'], self.tuckbox['height']),
                       (self.tuckbox['depth']*2 + self.tuckbox['width'],
                        self.tuckbox['height'] + self.tuckbox['depth']*.8),
                       (self.tuckbox['depth']*2 + self.tuckbox['width']*2,
                        self.tuckbox['height'] + self.tuckbox['depth']*.8),
                       (self.tuckbox['depth']*2 + self.tuckbox['width']*2,
                        self.tuckbox['height']),
                       (self.tuckbox['depth']*2.8 + self.tuckbox['width']*2,
                        self.tuckbox['height']),
                       (self.tuckbox['depth']*2.8 +
                        self.tuckbox['width']*2, 0),
                       (self.tuckbox['depth']*2 + self.tuckbox['width']*2, 0),
                       (self.tuckbox['depth']*2 +
                        self.tuckbox['width']*1.6, 0),
                       ])
        draw.polyline([(self.tuckbox['depth']*2 + self.tuckbox['width']*1.4, 0),
                       (self.tuckbox['depth']*2 + self.tuckbox['width'], 0),
                       (self.tuckbox['depth']*1.9 +
                        self.tuckbox['width'], -tab_length),
                       (self.tuckbox['depth']*1.1 +
                        self.tuckbox['width'], -tab_length),
                       (self.tuckbox['depth'] + self.tuckbox['width'], 0),
                       (self.tuckbox['depth'] +
                        self.tuckbox['width'], -self.tuckbox['depth']),
                       (self.tuckbox['depth'] + self.tuckbox['width']
                        * .8, -self.tuckbox['depth']),
                       ])

        # 1/2 left of lip
        draw.bezier([(self.tuckbox['depth'], -self.tuckbox['depth']),
                     (self.tuckbox['depth'], -
                      self.tuckbox['depth'] - .75 * self.lip_size()),
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
        if "folds_dashed" in self.options and self.options["folds_dashed"]:
            dashed_draw.stroke_color = Color('rgb(100,100,100)')
            dashed_draw.fill_opacity = 0
            dashed_draw.stroke_width = RESOLUTION / (300 * POINT_PER_MM)
            dashed_draw.stroke_dash_array = dash_array
            dashed_draw.stroke_dash_offset = 1
            dashed_draw.line(
                (0, 0), (self.tuckbox['depth']*2 + self.tuckbox['width'], 0))
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
            dashed_draw.line((self.tuckbox['depth']*2 + self.tuckbox['width']*2, 0),
                             (self.tuckbox['depth']*2 + self.tuckbox['width']*2, self.tuckbox['height']))

        if progress_tracker is not None:
            progress_tracker(10)

        # Create the image
        image = Image(width=math.ceil(self.paper['width'] * POINT_PER_MM),
                      height=math.ceil(self.paper['height'] * POINT_PER_MM),
                      background=Color('white'))
        image.resolution = RESOLUTION
        image.unit = 'pixelsperinch'

        # Draw the faces
        self.draw_faces(image, progress_tracker)

        # Draw the lip
        lip = self.draw_lip()
        if lip is not None:
            image.composite(lip,
                            math.floor((margin_width + self.tuckbox['depth']) * POINT_PER_MM),
                            math.floor((margin_height) * POINT_PER_MM))

        if progress_tracker is not None:
            progress_tracker(80)

        # Draw all the lines over
        draw.draw(image)

        if progress_tracker is not None:
            progress_tracker(90)

        finger_draw.draw(image)

        self.draw_watermark(image)

        if "folds_dashed" in self.options and self.options["folds_dashed"]:
            dashed_draw.draw(image)

        if "folding_guides" in self.options and self.options["folding_guides"]:
            folding_guides_draw = Drawing()
            folding_guides_draw.scale(POINT_PER_MM, POINT_PER_MM)

            folding_guides_draw.stroke_color = Color('black')
            folding_guides_draw.stroke_width = RESOLUTION / (200 * POINT_PER_MM)

            vertical_folds = [margin_width + self.tuckbox['depth'],
                              margin_width +
                              self.tuckbox['depth'] + self.tuckbox['width'],
                              margin_width +
                              self.tuckbox['depth']*2 + self.tuckbox['width'],
                              margin_width + self.tuckbox['depth']*2 + self.tuckbox['width']*2]
            vertical_folds_length = min(0.6 * margin_height, 20)
            for x in vertical_folds:
                folding_guides_draw.line(
                    (x, 0.6 * margin_height - vertical_folds_length), (x, 0.6 * margin_height))
                folding_guides_draw.line(
                    (x, self.paper['height'] - 0.6 * margin_height + vertical_folds_length), (x, self.paper['height'] - 0.6 * margin_height))

            horizontal_folds = [margin_height + self.lip_size(),
                                margin_height + self.lip_size() +
                                self.tuckbox['depth'],
                                margin_height + self.lip_size() +
                                self.tuckbox['depth'] + self.tuckbox['height']]
            horizontal_folds_length = min(0.6*margin_width, 20)
            for y in horizontal_folds:
                folding_guides_draw.line(
                    (0.6*margin_width - horizontal_folds_length, y), (0.6*margin_width, y))
                folding_guides_draw.line(
                    (self.paper['width'] - 0.6*margin_width + horizontal_folds_length, y), (self.paper['width'] - 0.6*margin_width, y))

            folding_guides_draw.draw(image)

        if progress_tracker is not None:
            progress_tracker(100)

        return image

    def draw_faces(self, image, progress_tracker):
        margin_height = (self.paper['height'] - self.pattern_height()) / 2
        margin_width = (self.paper['width'] - self.pattern_width()) / 2

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

        face_angles = {}
        face_smart_rescale = {}
        for face in ["front", "back", "left", "right", "top", "bottom"]:
            face_angles[face] = self.options[face +
                                             "_angle"] if face+"_angle" in self.options else 0
            face_smart_rescale[face] = self.options[face+"_smart_rescale"] if face + \
                "_smart_rescale" in self.options else False

        # Apply those face pictures
        for counter, side in enumerate(["front", "back", "left", "right", "top", "bottom"]):
            if side in self.faces:
                if self.faces[side][:1] == "#":
                    # we are filling with color
                    color_face_draw = Drawing()
                    color_face_draw.stroke_width = 0
                    color_face_draw.fill_color = Color(self.faces[side])
                    color_face_draw.rectangle(left = face_positions[side][0], top = face_positions[side][1],
                                            width = face_sizes[side][0], height = face_sizes[side][1])
                    color_face_draw.draw(image)
                else:
                    _, file_extension = os.path.splitext(os.path.basename(self.faces[side]))
                    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
                    self.resize_rotate_image(self.faces[side], tmp_file.name, face_smart_rescale[side], face_angles[side] * 90, *face_sizes[side])
                    with Image(filename=tmp_file.name) as i:
                        image.composite(i, *face_positions[side])

            if progress_tracker is not None:
                progress_tracker(10*(counter+2))

    def draw_lip(self):
        if "back" not in self.faces:
            return None

        # First draw a full mask with the lip shape
        lip_full_mask_image = Image(width=math.ceil(self.tuckbox['width'] * POINT_PER_MM),
                                    height=math.ceil(self.lip_size() * POINT_PER_MM))
        lip_full_draw = Drawing()

        lip_full_draw.scale(POINT_PER_MM, POINT_PER_MM)

        # This cannot be too "thin" or the floodfill later would spill over
        lip_full_draw.stroke_width = max(2 / POINT_PER_MM, RESOLUTION / (200 * POINT_PER_MM))

        lip_full_draw.fill_color = Color('white')
        lip_full_draw.color(0, 0, 'reset')
        lip_full_draw.draw(lip_full_mask_image)

        lip_full_draw.stroke_color = Color('black')

        # 1/2 left of lip
        lip_full_draw.bezier([(0, self.lip_size()),
                              (0, self.lip_size() - .75*self.lip_size()),
                              (.2 * self.tuckbox['width'],
                               self.lip_size() - self.lip_size()),
                              (.5 * self.tuckbox['width'], self.lip_size() - self.lip_size())])

        # 1/2 right of lip
        lip_full_draw.bezier([(self.tuckbox['width'], self.lip_size()),
                              (self.tuckbox['width'],
                               self.lip_size() - .75*self.lip_size()),
                              (.8 * self.tuckbox['width'],
                               self.lip_size() - self.lip_size()),
                              (.5 * self.tuckbox['width'], self.lip_size() - self.lip_size())])

        lip_full_draw.draw(lip_full_mask_image)

        lip_full_draw.fill_color = Color('black')
        lip_full_draw.border_color = Color('black')
        lip_full_draw.color(.5 * self.tuckbox['width'],
                            0.8*self.lip_size(), 'filltoborder')

        lip_full_draw.draw(lip_full_mask_image)

        if self.faces['back'][:1] == "#":
            lip_image = Image(width = lip_full_mask_image.width, height = lip_full_mask_image.height,
                            background = Color(self.faces['back']))
        else:
            # Prepare the front image
            if "back_angle" in self.options:
                angle = (self.options["back_angle"]+2)*90
            else:
                angle = 180

            _, file_extension = os.path.splitext(self.faces['back'])
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
            self.resize_rotate_image(self.faces['back'], tmp_file.name, "back_smart_rescale" in self.options and
                            self.options["back_smart_rescale"], angle, math.ceil(self.tuckbox['width'] * POINT_PER_MM),
                            math.ceil(self.tuckbox['height'] * POINT_PER_MM))
            lip_image = Image(filename=tmp_file.name)
            lip_image.crop(top=lip_image.height - lip_full_mask_image.height)

        # u = image pixel
        # h = height
        # j = row
        # Radius of the hold is {self.tuckbox['width']*.1}
        # if value is 1 (or more_, it's white
        # Top is the tip of the lip, bottom is attached to the box
        # finger_hold_size_save is the row # at which it should be no attenuation below
        finger_hold_size_save = str(
            int(lip_image.height - math.ceil(self.tuckbox['width'] * POINT_PER_MM * 0.1)))
        lip_image = lip_image.fx(
            "j>"+finger_hold_size_save+"?u:1+(u-1)*(j/"+finger_hold_size_save+")")

        lip_image.composite(operator='lighten', image=lip_full_mask_image)

        return lip_image

    def resize_rotate_image(self, filename, destination_filename, smart_rescale = False, angle=0, width=0, height=0):
        # convert filename [-rotate angle] [-liquid-rescale|-resize widthxheight!] destination_filename
        cmd = ["convert"]
        cmd.append(filename)
        if angle == 0 and (width == 0 or height == 0):
            return
        if angle != 0:
            cmd.append("-rotate")
            cmd.append("{}".format(int(angle)))
        if width != 0 and height != 0:
            cmd.append("-resize")
            cmd.append("{}x{}!".format(int(width), int(height)))
        cmd.append(destination_filename)
        #print("running the command {}".format(cmd))
        subprocess.run(cmd)
        #print("done")


    def draw_watermark(self, img):
        watermark_draw = Drawing()
        watermark_draw.stroke_color = Color('black')
        watermark_draw.font = os.path.join(os.path.dirname(__file__), "Colombia-Regular.ttf")
        watermark_draw.font_size = 3 * POINT_PER_MM
        watermark_draw.text_antialias = True
        metrics = watermark_draw.get_font_metrics(img, WATERMARK)
        watermark_draw.text(max(0, math.floor((POINT_PER_MM * self.paper['width']) - metrics.text_width)),
                            max(0, math.floor((POINT_PER_MM * self.paper['height']) - metrics.text_height)),
                            WATERMARK)
        watermark_draw.draw(img)
