import os
from django.test import TestCase
from wand.image import Image
from tuckbox import box

comparison_metric = 'perceptual_hash'
comparison_threshold = 10  # This allows to change resolution of the output

class BoxTestCase(TestCase):
    def compare_images(self, test_filename, my_box, save_image):
        test_file = os.path.join(os.path.dirname(__file__), test_filename)

        if save_image:
            my_box.create_box_file(test_file)
            return

        i = my_box.draw_box()
        ref_image = Image(filename=test_file)
        i.resize(ref_image.width, ref_image.height)
        _, compare_metric = i.compare(ref_image, metric=comparison_metric)

        #print("For file " + test_filename + ", got error "+str(compare_metric))
        self.assertLessEqual(compare_metric, comparison_threshold)

    def test_DrawSimpleWhite(self, save_image = False):
        test_file = "test_simple_white.png"
        paper = {'width': 200, 'height': 200}
        tuckbox = {'height': 70, 'width': 50, 'depth': 20}
        my_box = box.TuckBoxDrawing(tuckbox, paper, None, None)

        self.compare_images(test_file, my_box, save_image)

    def test_DrawSimpleWithDash(self, save_image = False):
        test_file = "test_simple_dashes.png"
        paper = {'width': 200, 'height': 200}
        tuckbox = {'height': 70, 'width': 50, 'depth': 20}
        options = {'folds_dashed': True}
        my_box = box.TuckBoxDrawing(tuckbox, paper, None, options)

        self.compare_images(test_file, my_box, save_image)

    def test_DrawSimpleWithGuides(self, save_image = False):
        test_file = "test_simple_guides.png"
        paper = {'width': 200, 'height': 200}
        tuckbox = {'height': 70, 'width': 50, 'depth': 20}
        options = {'folding_guides': True}
        my_box = box.TuckBoxDrawing(tuckbox, paper, options = options)

        self.compare_images(test_file, my_box, save_image)

    def test_DrawAdjustLayout(self, save_image = False):
        test_file = "test_adjust_layout.png"
        paper = {'width': 200, 'height': 150}
        tuckbox = {'height': 100, 'width': 40, 'depth': 20}
        my_box = box.TuckBoxDrawing(tuckbox, paper)

        self.compare_images(test_file, my_box, save_image)

    def test_DrawWithFaces(self, save_image=False):
        test_file = "test_faces.png"
        paper = {'width': 200, 'height': 200}
        tuckbox = {'height': 70, 'width': 50, 'depth': 20}
        with open(os.path.join(os.path.dirname(__file__),"front.jpg"), "rb") as front, open(os.path.join(os.path.dirname(__file__),"back.jpg"), "rb") as back, open(os.path.join(os.path.dirname(__file__),"left.jpg"), "rb") as left, open(os.path.join(os.path.dirname(__file__),"right.jpg"), "rb") as right, open(os.path.join(os.path.dirname(__file__),"top.jpg"), "rb") as top, open(os.path.join(os.path.dirname(__file__),"bottom.jpg"), "rb") as bottom:
            faces = {'front': front, 'back': back, 'left': left,
                    'right': right, 'top': top, 'bottom': bottom}
            my_box = box.TuckBoxDrawing(tuckbox, paper, faces = faces)

            self.compare_images(test_file, my_box, save_image)

    def test_DrawWithRotations(self, save_image=False):
        test_file = "test_rotation.png"
        paper = {'width': 200, 'height': 200}
        tuckbox = {'height': 70, 'width': 50, 'depth': 20}
        with open(os.path.join(os.path.dirname(__file__),"front.jpg"), "rb") as front, open(os.path.join(os.path.dirname(__file__),"back.jpg"), "rb") as back, open(os.path.join(os.path.dirname(__file__),"left.jpg"), "rb") as left, open(os.path.join(os.path.dirname(__file__),"right.jpg"), "rb") as right, open(os.path.join(os.path.dirname(__file__),"top.jpg"), "rb") as top, open(os.path.join(os.path.dirname(__file__),"bottom.jpg"), "rb") as bottom:
            faces = {'front': front, 'back': back, 'left': left,
                    'right': right, 'top': top, 'bottom': bottom}
            options = {'front_angle': 1, 'back_angle': 2, 'left_angle': 3,
                       'right_angle': 1, 'top_angle': 2, 'bottom_angle': 3}
            my_box = box.TuckBoxDrawing(tuckbox, paper, faces = faces, options = options)

            self.compare_images(test_file, my_box, save_image)

    def test_DrawResize(self, save_image=False):
        test_file = "test_resize.png"
        paper = {'width': 200, 'height': 200}
        tuckbox = {'height': 70, 'width': 50, 'depth': 20}
        with open(os.path.dirname(__file__)+"/house.png", "rb") as house:
            faces = {'front': house}
            options = {'front_smart_rescale': True}
            my_box = box.TuckBoxDrawing(tuckbox, paper, faces = faces, options = options)

            self.compare_images(test_file, my_box, save_image)

    def test_Fit(self):
        paper = {'width': 100, 'height': 100}
        tuckbox = {'height': 30, 'width': 20, 'depth': 10}
        my_box = box.TuckBoxDrawing(tuckbox, paper)
        self.assertTrue(my_box.will_it_fit())

        tuckbox = {'height': 80, 'width': 20, 'depth': 20}
        my_box = box.TuckBoxDrawing(tuckbox, paper)
        self.assertFalse(my_box.will_it_fit())

        tuckbox = {'height': 30, 'width': 50, 'depth': 20}
        my_box = box.TuckBoxDrawing(tuckbox, paper)
        self.assertFalse(my_box.will_it_fit())


if __name__ == "__main__":
    # Generate the test files
    test_class = BoxTestCase()
    object_methods = [method_name for method_name in dir(BoxTestCase)
                  if callable(getattr(BoxTestCase, method_name))]
    test_methods = list(filter(lambda s: s.startswith("test_Draw"), object_methods))
    for method_name in test_methods:
        method_to_call = getattr(test_class, method_name)
        method_to_call(True)