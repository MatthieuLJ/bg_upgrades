import math
import os
import stat
import subprocess
import sys
import tempfile
from pypdf import PdfWriter
from wand.api import library
from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image
from wand.resource import limits


RESOLUTION = 600  # Dots Per Inch
POINT_PER_MM = RESOLUTION / 25.4  # 25.4 mm per inch
WATERMARK = "Tuckbox generated @ https://www.bg-upgrades.net/  "


class TuckBoxDrawing:
    def __init__(self, tuckbox, paper, faces=None, options=None):
        self.tuckbox = tuckbox
        self.paper = paper
        self.faces = faces if faces is not None else {}
        self.options = options if options is not None else {}

        # Use disk when using more than 100MB of memory
        limits['memory'] = 100 * 1024 * 1024

    def create_box_file(self, filename, progress_tracker=None):
        image, image2 = self.draw_box(progress_tracker)

        if image is not None and image2 is None:
            image.save(filename=filename)
            os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        elif image is not None and image2 is not None:
            filename1 = filename[0:-4] + "_1" + filename[-4:]
            filename2 = filename[0:-4] + "_2" + filename[-4:]
            image.save(filename=filename1)
            os.chmod(filename1, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            image2.save(filename=filename2)
            os.chmod(filename2, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

            if filename[-3:].lower() == 'pdf':
                merger = PdfWriter()
                merger.append(filename1)
                merger.append(filename2)

                merger.write(filename)
                merger.close()
                os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

    def lip_size(self):
        # the lip is the minimum of
        # the depth
        # 30% of the width
        return min(self.tuckbox['depth'], .3 * self.tuckbox['width'])

    def pattern_height(self):
        if 'two_openings' in self.options and self.options['two_openings']:
            return self.tuckbox['height'] + (2 * self.tuckbox['depth']) + (2 * self.lip_size())
        else:
            return self.tuckbox['height'] + (2 * self.tuckbox['depth']) + self.lip_size()

    def pattern_width(self):
        if 'two_pages' in self.options and self.options['two_pages']:
            return self.tuckbox['width'] + (2 * self.tuckbox['depth'])
        else:
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

        # How much white space on the sides
        margin_height = (self.paper['height'] - self.pattern_height()) / 2
        margin_width = (self.paper['width'] - self.pattern_width()) / 2

        # Main box draw
        draw = Drawing()
        draw.scale(POINT_PER_MM, POINT_PER_MM)
        draw.stroke_color = Color('black')
        draw.stroke_width = RESOLUTION / (200 * POINT_PER_MM)
        draw.fill_opacity = 0
        draw.translate(margin_width,
                       margin_height + self.lip_size() + self.tuckbox['depth'])
        draw.push()

        # Finger holds draw
        finger_draw = Drawing(draw)
        finger_draw.fill_opacity = 1
        finger_draw.fill_color = Color('white')
        finger_draw.push()

        # Dashed draw
        dashed_draw = Drawing(draw)
        dash_array = [min(self.tuckbox['depth'], self.tuckbox['width'],
                          self.tuckbox['height'])/13] * 2
        dashed_draw.stroke_color = Color('rgb(100,100,100)')
        dashed_draw.fill_opacity = 0
        dashed_draw.stroke_width = RESOLUTION / (300 * POINT_PER_MM)
        dashed_draw.stroke_dash_array = dash_array
        dashed_draw.stroke_dash_offset = 1

        # Folding guides draw
        folding_guides_draw = Drawing()
        folding_guides_draw.scale(POINT_PER_MM, POINT_PER_MM)
        folding_guides_draw.stroke_color = Color('black')
        folding_guides_draw.stroke_width = RESOLUTION / (200 * POINT_PER_MM)

        back_draw = Drawing(draw)
        back_dashed_draw = Drawing(dashed_draw)
        back_folding_guides_draw = Drawing(folding_guides_draw)

        if progress_tracker is not None:
            progress_tracker(5)

        two_openings = 'two_openings' in self.options and self.options['two_openings']
        two_pages = 'two_pages' in self.options and self.options['two_pages']

        dash_array = [min(self.tuckbox['depth'], self.tuckbox['width'],
                          self.tuckbox['height'])/13] * 2

        #
        # Draw the box (or the first page)
        #
        self.draw_front(draw, dashed_draw, two_openings)

        if two_pages:
            offset_left_to_back = self.tuckbox['depth']
        else:
            offset_left_to_back = self.tuckbox['depth']*2 + self.tuckbox['width']

        self.draw_back(offset_left_to_back, back_draw, back_dashed_draw, finger_draw, two_openings)

        if two_pages:
            back_draw.polyline([(self.tuckbox['depth'], 0),
                           (self.tuckbox['depth'] * 0.2, 0),
                           (self.tuckbox['depth'] * 0.2, self.tuckbox['height']),
                           (self.tuckbox['depth'], self.tuckbox['height'])])
            draw.line((self.tuckbox['depth']*2 + self.tuckbox['width'], 0),
                      (self.tuckbox['depth']*2 + self.tuckbox['width'], self.tuckbox['height']))

        if progress_tracker is not None:
            progress_tracker(10)

        # Create the image
        image = Image(width=math.ceil(self.paper['width'] * POINT_PER_MM),
                      height=math.ceil(self.paper['height'] * POINT_PER_MM),
                      background=Color('white'))
        image.resolution = RESOLUTION
        image.unit = 'pixelsperinch'

        if two_pages:
            image2 = Image(width=math.ceil(self.paper['width'] * POINT_PER_MM),
                        height=math.ceil(self.paper['height'] * POINT_PER_MM),
                        background=Color('white'))
            image2.resolution = RESOLUTION
            image2.unit = 'pixelsperinch'
        else:
            image2 = image

        # Draw the faces
        self.draw_faces(image, progress_tracker, with_back = not two_pages)
        if two_pages:
            self.draw_faces(image2, progress_tracker, only_back=True)

        # Draw the lip(s)
        lip = self.draw_lip(top=True)
        if lip is not None:
            image.composite(lip,
                            math.floor((margin_width + self.tuckbox['depth']) * POINT_PER_MM),
                            math.floor((margin_height) * POINT_PER_MM))

        if two_openings:
            lip = self.draw_lip(bottom=True)
            if lip is not None:
                image.composite(lip,
                                math.floor((margin_width + self.tuckbox['depth']) * POINT_PER_MM),
                                math.floor((margin_height + self.tuckbox['depth']*2 + self.lip_size() + self.tuckbox['height']) * POINT_PER_MM))

        if progress_tracker is not None:
            progress_tracker(80)

        # Draw all the lines over
        draw.draw(image)
        back_draw.draw(image2)

        finger_draw.draw(image2)
        self.draw_watermark(image)
        if two_pages:
            self.draw_watermark(image2)

        if progress_tracker is not None:
            progress_tracker(90)

        if "folds_dashed" in self.options and self.options["folds_dashed"]:
            dashed_draw.draw(image)
            back_dashed_draw.draw(image2)

        if "folding_guides" in self.options and self.options["folding_guides"]:
            front_vertical_folds = [margin_width + self.tuckbox['depth'],
                              margin_width +
                              self.tuckbox['depth'] + self.tuckbox['width']]
            if not two_pages:
                front_vertical_folds.extend([margin_width +
                                       self.tuckbox['depth']*2 + self.tuckbox['width'],
                                       margin_width + self.tuckbox['depth']*2 + self.tuckbox['width']*2])

            back_vertical_folds = [margin_width + self.tuckbox['depth'],
                                  margin_width +
                                  self.tuckbox['depth'] + self.tuckbox['width']]

            front_horizontal_folds = [margin_height + self.lip_size(),
                                margin_height + self.lip_size() +
                                self.tuckbox['depth'],
                                margin_height + self.lip_size() +
                                self.tuckbox['depth'] + self.tuckbox['height']]

            if two_openings:
                front_horizontal_folds.append(margin_height + self.lip_size() +
                                        self.tuckbox['depth'] * 2 + self.tuckbox['height'])
                back_horizontal_folds = []
            else:
                back_horizontal_folds = [margin_height + self.lip_size() +
                                        self.tuckbox['depth'] + self.tuckbox['height']]

            self.draw_folds(folding_guides_draw, front_vertical_folds, front_horizontal_folds, margin_height, margin_width)
            self.draw_folds(back_folding_guides_draw, back_vertical_folds, back_horizontal_folds, margin_height, margin_width)

            folding_guides_draw.draw(image)
            back_folding_guides_draw.draw(image2)

        if progress_tracker is not None:
            progress_tracker(100)

        if not two_pages:
            image2 = None

        return image, image2

    def draw_faces(self, image, progress_tracker, with_back=True, only_back=False):
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

        if only_back:
            faces = ["back"]
            # We are drawing the second page with the back face only, making some assumptions on its position
            face_positions["back"] = (math.floor((margin_width + self.tuckbox['depth']) * POINT_PER_MM),
                        math.floor((margin_height + self.lip_size() + self.tuckbox['depth']) * POINT_PER_MM))
        else:
            faces = list(face_sizes.keys())
            if not with_back:
                faces.remove("back")

        face_angles = {}
        for face in faces:
            face_angles[face] = self.options[face +
                                             "_angle"] if face+"_angle" in self.options else 0

        # Apply those face pictures
        for counter, side in enumerate(faces):
            if side in self.faces:
                if self.faces[side][:2] == "0x":
                    # we are filling with color
                    color_face_draw = Drawing()
                    color_face_draw.stroke_width = 0
                    color_face_draw.fill_color = Color("#"+self.faces[side][2:])
                    color_face_draw.rectangle(left = face_positions[side][0], top = face_positions[side][1],
                                            width = face_sizes[side][0], height = face_sizes[side][1])
                    color_face_draw.draw(image)
                # For some reason, the parameters of colors don't seem to be consistent
                elif self.faces[side][0] == "#":
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
                    self.resize_rotate_image(self.faces[side], tmp_file.name, face_angles[side] * 90, *face_sizes[side])
                    with Image(filename=tmp_file.name) as i:
                        image.composite(i, *face_positions[side])

            if progress_tracker is not None:
                progress_tracker(10*(counter+2))

    def draw_front(self, draw, dashed_draw, two_openings):
        #        ---------
        #       /         \
        #      +--S - - ---+
        #  +---+           +---+
        #  |   |           |   |
        #  0- - - - - - - - - -V
        #  |   |           |
        #  |
        #  |   |           |
        #  |
        #  |   |           |
        #  |
        #  |   |           |
        #  |
        #  |   |           |
        #  +- -T- - - - - -U- -+
        #  |   |           |   |
        #  +---+           +----
        #      +-----------+
        #
        #        ---------
        #       /         \
        #      +--S - - ---+
        #  +---+           +---+
        #  |   |           |   |
        #  0- - - - - - - - - -V
        #  |   |           |
        #  |
        #  |   |           |
        #  |
        #  |   |           |
        #  |
        #  |   |           |
        #  |
        #  |   |           |
        #  +- -T- - - - - -U- -+
        #  |   |           |   |
        #  +---+           +----
        #      +--- - - ---+
        #       \         /
        #        ---------
        #
        # 0 is the origin
        # S is the start of the first polyline (going counter-clockwise)
        # T, U, V, W, X are the start of the subsequent ones (between T-U and V-W would change if there are two openings)

        tab_length = min(.9 *
                         self.tuckbox['depth'], .4 * self.tuckbox['width'])
        # Draw the solid lines (S)
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
                       (self.tuckbox['depth'], self.tuckbox['height'])])

        # bottom flap (T)
        if two_openings:
            draw.polyline([(self.tuckbox['depth'], self.tuckbox['height']),
                           (self.tuckbox['depth'],
                            self.tuckbox['height'] + self.tuckbox['depth']),
                           (self.tuckbox['depth'] + self.tuckbox['width']*.2,
                            self.tuckbox['height'] + self.tuckbox['depth'])])
            draw.polyline([(self.tuckbox['depth'] + self.tuckbox['width']*.8,
                            self.tuckbox['height'] + self.tuckbox['depth']),
                           (self.tuckbox['depth'] + self.tuckbox['width'],
                            self.tuckbox['height'] + self.tuckbox['depth']),
                           (self.tuckbox['depth'] + self.tuckbox['width'],
                            self.tuckbox['height'])])

            # 1/2 left of bottom lip
            draw.bezier([(self.tuckbox['depth'], self.tuckbox['height'] + self.tuckbox['depth']),
                        (self.tuckbox['depth'], self.tuckbox['height'] + self.tuckbox['depth'] + .75 * self.lip_size()),
                        (self.tuckbox['depth'] + .2 * self.tuckbox['width'],
                        self.tuckbox['height'] + self.tuckbox['depth'] + self.lip_size()),
                        (self.tuckbox['depth'] + .5 * self.tuckbox['width'],
                        self.tuckbox['height'] + self.tuckbox['depth'] + self.lip_size())])

            # 1/2 right of bottom lip
            draw.bezier([(self.tuckbox['depth'] + self.tuckbox['width'], self.tuckbox['height'] + self.tuckbox['depth']),
                        (self.tuckbox['depth'] + self.tuckbox['width'],
                        self.tuckbox['height'] + self.tuckbox['depth'] + .75*self.lip_size()),
                        (self.tuckbox['depth'] + .8 * self.tuckbox['width'],
                        self.tuckbox['height'] + self.tuckbox['depth'] + self.lip_size()),
                        (self.tuckbox['depth'] + .5 * self.tuckbox['width'],
                        self.tuckbox['height'] + self.tuckbox['depth'] + self.lip_size())])
        else:
            draw.polyline([(self.tuckbox['depth'], self.tuckbox['height']),
                           (self.tuckbox['depth'],
                            self.tuckbox['height'] + self.tuckbox['depth']),
                           (self.tuckbox['depth'] + self.tuckbox['width'],
                            self.tuckbox['height'] + self.tuckbox['depth']),
                           (self.tuckbox['depth'] + self.tuckbox['width'],
                            self.tuckbox['height'])])

        # Keep going around (U)
        draw.polyline([(self.tuckbox['depth'] + self.tuckbox['width'],
                        self.tuckbox['height']),
                       (self.tuckbox['depth']*1.1 + self.tuckbox['width'],
                        self.tuckbox['height'] + tab_length),
                       (self.tuckbox['depth']*1.9 + self.tuckbox['width'],
                        self.tuckbox['height'] + tab_length),
                       (self.tuckbox['depth']*2 +
                        self.tuckbox['width'], self.tuckbox['height'])])

        # Restart higher (V)
        draw.polyline([(self.tuckbox['depth']*2 + self.tuckbox['width'], 0),
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

        # 1/2 left of top lip
        draw.bezier([(self.tuckbox['depth'], -self.tuckbox['depth']),
                     (self.tuckbox['depth'], -
                      self.tuckbox['depth'] - .75 * self.lip_size()),
                     (self.tuckbox['depth'] + .2 * self.tuckbox['width'],
                      -self.tuckbox['depth'] - self.lip_size()),
                     (self.tuckbox['depth'] + .5 * self.tuckbox['width'],
                      -self.tuckbox['depth'] - self.lip_size())])

        # 1/2 right of top lip
        draw.bezier([(self.tuckbox['depth'] + self.tuckbox['width'], -self.tuckbox['depth']),
                     (self.tuckbox['depth'] + self.tuckbox['width'],
                      -self.tuckbox['depth'] - .75*self.lip_size()),
                     (self.tuckbox['depth'] + .8 * self.tuckbox['width'],
                      -self.tuckbox['depth'] - self.lip_size()),
                     (self.tuckbox['depth'] + .5 * self.tuckbox['width'],
                      -self.tuckbox['depth'] - self.lip_size())])
        # dashed lines
        if "folds_dashed" in self.options and self.options['folds_dashed']:
            dashed_draw.line((0, 0),
                             (self.tuckbox['depth']*2 + self.tuckbox['width'], 0))
            dashed_draw.line((self.tuckbox['depth'] + self.tuckbox['width']*.2, -self.tuckbox['depth']),
                             (self.tuckbox['depth'] + self.tuckbox['width']*.8, -self.tuckbox['depth']))
            if two_openings:
                dashed_draw.line((self.tuckbox['depth'] + self.tuckbox['width']*.2, self.tuckbox['height']+self.tuckbox['depth']),
                                 (self.tuckbox['depth'] + self.tuckbox['width']*.8, self.tuckbox['height']+self.tuckbox['depth']))
            dashed_draw.line((0, self.tuckbox['height']),
                             (self.tuckbox['depth']*2 + self.tuckbox['width'], self.tuckbox['height']))
            dashed_draw.line((self.tuckbox['depth'], 0),
                             (self.tuckbox['depth'], self.tuckbox['height']))
            dashed_draw.line((self.tuckbox['depth'] + self.tuckbox['width'], 0),
                             (self.tuckbox['depth'] + self.tuckbox['width'], self.tuckbox['height']))
    def draw_back(self, offset_left, draw, dashed_draw, finger_draw, two_openings):
        #  +----X +----+--+
        #  |    +-+    |  |
        #                 |
        #  |           |  |
        #                 |
        #  |           |  |
        #                 |
        #  |           |  |
        #                 |
        #  |           |  |
        #  V- - - - - -W--+
        #  |           |
        #  ------------+

        #  +----X +----+--+
        #  |    +-+    |  |
        #                 |
        #  |           |  |
        #                 |
        #  |           |  |
        #                 |
        #  |           |  |
        #                 |
        #  |    +-+    |  |
        #  V- - + + - -W--+

        # Last bit before the notch (X)
        draw.polyline([(offset_left, 0),
                       (offset_left + self.tuckbox['width']*0.4, 0)])

        # Keep going around (W)
        draw.polyline([(offset_left + self.tuckbox['width'],
                        self.tuckbox['height']),
                       (offset_left + self.tuckbox['depth']*0.8 + self.tuckbox['width'],
                        self.tuckbox['height']),
                       (offset_left + self.tuckbox['depth']*0.8 +
                        self.tuckbox['width'], 0),
                       (offset_left + self.tuckbox['width']*0.6, 0),
                       ])

        # bottom of back (V)
        if two_openings:
            # before the notch
            draw.polyline([(offset_left, self.tuckbox['height']),
                           (offset_left + self.tuckbox['width']*0.4, self.tuckbox['height'])])
            # after the notch
            draw.polyline([(offset_left + self.tuckbox['width']*0.6, self.tuckbox['height']),
                           (offset_left + self.tuckbox['width'], self.tuckbox['height'])])
        else:
            draw.polyline([(offset_left, self.tuckbox['height']),
                           (offset_left,
                            self.tuckbox['height'] + self.tuckbox['depth']*.8),
                           (offset_left + self.tuckbox['width'],
                            self.tuckbox['height'] + self.tuckbox['depth']*.8),
                           (offset_left + self.tuckbox['width'],
                            self.tuckbox['height'])])
        finger_draw.arc((offset_left + self.tuckbox['width']*0.4, -self.tuckbox['width']*.1),
                        (offset_left + self.tuckbox['width']
                         * 0.6, self.tuckbox['width']*.1),
                        (0, 180))

        if two_openings:
            # bottom finger hold
            finger_draw.arc((offset_left + self.tuckbox['width']*0.4,
                             self.tuckbox['height'] - self.tuckbox['width']*.1),
                            (offset_left + self.tuckbox['width'] * 0.6, self.tuckbox['height'] + self.tuckbox['width']*.1),
                            (180, 0))

        # dashed lines
        if "folds_dashed" in self.options and self.options['folds_dashed']:
            if not two_openings:
                dashed_draw.line((offset_left, self.tuckbox['height']),
                                 (offset_left + self.tuckbox['width'], self.tuckbox['height']))
            dashed_draw.line((offset_left, 0),
                             (offset_left, self.tuckbox['height']))
            dashed_draw.line((offset_left + self.tuckbox['width'], 0),
                             (offset_left + self.tuckbox['width'], self.tuckbox['height']))

    def draw_lip(self, top=False, bottom=False):
        if "back" not in self.faces:
            return None

        if not (top ^ bottom): # 1 and only 1 of top or bottom should be true
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

        if self.faces['back'][:2] == "0x":
            lip_image = Image(width = lip_full_mask_image.width, height = lip_full_mask_image.height,
                            background = Color("#"+self.faces['back'][2:]))
        elif self.faces['back'][0] == "#":
            lip_image = Image(width = lip_full_mask_image.width, height = lip_full_mask_image.height,
                            background = Color(self.faces['back']))
        else:
            # Prepare the front image
            angle = 180 if "back_angle" not in self.options else (self.options["back_angle"]+2)*90

            if bottom:
                angle = (angle + 180) % 360

            _, file_extension = os.path.splitext(self.faces['back'])
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
            self.resize_rotate_image(self.faces['back'], tmp_file.name, angle, math.ceil(self.tuckbox['width'] * POINT_PER_MM),
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

        if bottom:
            lip_image.rotate(180)

        return lip_image

    def draw_folds(self, folding_guides_draw, vertical_folds, horizontal_folds, margin_height, margin_width):
        vertical_folds_length = min(0.6 * margin_height, 20)
        for x in vertical_folds:
            folding_guides_draw.line(
                (x, 0.6 * margin_height - vertical_folds_length), (x, 0.6 * margin_height))
            folding_guides_draw.line(
                (x, self.paper['height'] - 0.6 * margin_height + vertical_folds_length), (x, self.paper['height'] - 0.6 * margin_height))

        horizontal_folds_length = min(0.6*margin_width, 20)
        for y in horizontal_folds:
            folding_guides_draw.line(
                (0.6*margin_width - horizontal_folds_length, y), (0.6*margin_width, y))
            folding_guides_draw.line(
                (self.paper['width'] - 0.6*margin_width + horizontal_folds_length, y), (self.paper['width'] - 0.6*margin_width, y))

    def resize_rotate_image(self, filename, destination_filename, angle=0, width=0, height=0):
        # convert filename [-rotate angle] [-resize widthxheight!] destination_filename
        cmd = ["magick"]
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
                            max(0, math.floor((POINT_PER_MM * self.paper['height']) - metrics.text_height * 2)),
                            WATERMARK)
        watermark_draw.draw(img)
