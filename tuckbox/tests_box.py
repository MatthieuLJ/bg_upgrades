import os
from django.test import TestCase
from wand.image import Image
from tuckbox import box


class BoxTestCase(TestCase):
    def test_DrawSimpleWhite(self, save_image = False):
        test_file = os.path.dirname(__file__) + "/test_simple_white.png"
        paper = {'width': 100, 'height': 100}
        tuckbox = {'height': 30, 'width': 20, 'depth': 10}
        my_box = box.TuckBoxDrawing(tuckbox, paper, None, None)

        if save_image:
            my_box.create_box_file(test_file)
            return

        i = my_box.draw_box()
        i.fuzz = i.quantum_range * 0.05
        ref_image = Image(filename=test_file)
        _, compare_metric = i.compare(ref_image, metric='absolute')

        self.assertLess(compare_metric, 1.0)

    def test_DrawSimpleWithDash(self, save_image = False):
        test_file = os.path.dirname(__file__) + "/test_simple_dashes.png"
        paper = {'width': 100, 'height': 100}
        tuckbox = {'height': 30, 'width': 20, 'depth': 10}
        options = {'folds_dashed': True}
        my_box = box.TuckBoxDrawing(tuckbox, paper, None, options)

        if save_image:
            my_box.create_box_file(test_file)
            return

        i = my_box.draw_box()
        i.fuzz = i.quantum_range * 0.05
        ref_image = Image(filename=test_file)
        _, compare_metric = i.compare(ref_image, metric='absolute')

        self.assertLess(compare_metric, 1.0)

    def test_DrawSimpleWithGuides(self, save_image = False):
        test_file = os.path.dirname(__file__) + "/test_simple_guides.png"
        paper = {'width': 100, 'height': 100}
        tuckbox = {'height': 30, 'width': 20, 'depth': 10}
        options = {'folding_guides': True}
        my_box = box.TuckBoxDrawing(tuckbox, paper, options = options)

        if save_image:
            my_box.create_box_file(test_file)
            return

        i = my_box.draw_box()
        i.fuzz = i.quantum_range * 0.05
        ref_image = Image(filename=test_file)
        _, compare_metric = i.compare(ref_image, metric='absolute')

        self.assertLess(compare_metric, 1.0)

    def test_DrawAdjustLayout(self, save_image = False):
        test_file = os.path.dirname(__file__) + "/test_adjust_layout.png"
        paper = {'width': 200, 'height': 150}
        tuckbox = {'height': 100, 'width': 40, 'depth': 20}
        my_box = box.TuckBoxDrawing(tuckbox, paper)
        if save_image:
            my_box.create_box_file(test_file)
            return

        i = my_box.draw_box()
        i.fuzz = i.quantum_range * 0.05
        ref_image = Image(filename=test_file)
        _, compare_metric = i.compare(ref_image, metric='absolute')

        self.assertLess(compare_metric, 1.0)

    def test_DrawWithFaces(self, save_image=False):
        test_file = os.path.dirname(__file__) + "/test_faces.png"
        paper = {'width': 100, 'height': 100}
        tuckbox = {'height': 30, 'width': 20, 'depth': 10}
        with open(os.path.dirname(__file__)+"/front.jpg", "rb") as front, open(os.path.dirname(__file__)+"/back.jpg", "rb") as back, open(os.path.dirname(__file__)+"/left.jpg", "rb") as left, open(os.path.dirname(__file__)+"/right.jpg", "rb") as right, open(os.path.dirname(__file__)+"/top.jpg", "rb") as top, open(os.path.dirname(__file__)+"/bottom.jpg", "rb") as bottom:
            faces = {'front': front, 'back': back, 'left': left,
                    'right': right, 'top': top, 'bottom': bottom}
            my_box = box.TuckBoxDrawing(tuckbox, paper, faces = faces)

            if save_image:
                my_box.create_box_file(test_file)
                return

            i = my_box.draw_box()
            i.fuzz = i.quantum_range * 0.05
            ref_image = Image(filename=test_file)
            _, compare_metric = i.compare(ref_image, metric='absolute')

            self.assertLess(compare_metric, 1.0)

    def test_DrawWithRotations(self, save_image=False):
        test_file = os.path.dirname(__file__) + "/test_rotation.png"
        paper = {'width': 100, 'height': 100}
        tuckbox = {'height': 30, 'width': 20, 'depth': 10}
        with open(os.path.dirname(__file__)+"/front.jpg", "rb") as front, open(os.path.dirname(__file__)+"/back.jpg", "rb") as back, open(os.path.dirname(__file__)+"/left.jpg", "rb") as left, open(os.path.dirname(__file__)+"/right.jpg", "rb") as right, open(os.path.dirname(__file__)+"/top.jpg", "rb") as top, open(os.path.dirname(__file__)+"/bottom.jpg", "rb") as bottom:
            faces = {'front': front, 'back': back, 'left': left,
                    'right': right, 'top': top, 'bottom': bottom}
            options = {'front_angle': 1, 'back_angle': 2, 'left_angle': 3,
                       'right_angle': 1, 'top_angle': 2, 'bottom_angle': 3}
            my_box = box.TuckBoxDrawing(tuckbox, paper, faces, options)

            if save_image:
                my_box.create_box_file(test_file)
                return

            i = my_box.draw_box()
            i.fuzz = i.quantum_range * 0.05
            ref_image = Image(filename=test_file)
            _, compare_metric = i.compare(ref_image, metric='absolute')

            self.assertLess(compare_metric, 1.0)

    def test_DrawResize(self, save_image=False):
        test_file = os.path.dirname(__file__) + "/test_resize.png"
        paper = {'width': 100, 'height': 100}
        tuckbox = {'height': 30, 'width': 20, 'depth': 10}
        with open(os.path.dirname(__file__)+"/house.png", "rb") as house:
            faces = {'front': house}
            options = {'front_smart_rescale': True}
            my_box = box.TuckBoxDrawing(tuckbox, paper, faces, options)

            if save_image:
                my_box.create_box_file(test_file)
                return

            i = my_box.draw_box()
            i.fuzz = i.quantum_range * 0.05
            ref_image = Image(filename=test_file)
            _, compare_metric = i.compare(ref_image, metric='absolute')

            self.assertLess(compare_metric, 1.0)


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