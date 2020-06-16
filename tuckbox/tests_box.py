import os
from django.test import TestCase
from wand.image import Image
from tuckbox import box


class BoxTestCase(TestCase):
    def test_AdjustLayout(self, save_image = False):
        test_file = os.path.dirname(__file__) + "/test_adjust_layout.png"
        paper = {'width': 210, 'height': 297}
        tuckbox = {'height': 100, 'width': 80, 'depth': 40}
        my_box = box.TuckBoxDrawing(tuckbox, paper, None, None)
        if save_image:
            my_box.create_box_file(test_file)
            return

        i = my_box.draw_box()
        i.fuzz = i.quantum_range * 0.05
        ref_image = Image(filename=test_file)
        _, compare_metric = i.compare(ref_image, metric='absolute')

        self.assertLess(compare_metric, 1.0)
        

    def test_SimpleWhite(self, save_image = False):
        test_file = os.path.dirname(__file__) + "/test_simple_white.png"
        paper = {'width': 210, 'height': 297}
        tuckbox = {'height': 50, 'width': 40, 'depth': 30}
        my_box = box.TuckBoxDrawing(tuckbox, paper, None, None)

        if save_image:
            my_box.create_box_file(test_file)
            return

        i = my_box.draw_box()
        i.fuzz = i.quantum_range * 0.05
        ref_image = Image(filename=test_file)
        _, compare_metric = i.compare(ref_image, metric='absolute')

        self.assertLess(compare_metric, 1.0)

    def test_withFaces(self, save_image=False):
        test_file = os.path.dirname(__file__) + "/test_faces.png"
        paper = {'width': 100, 'height': 100}
        tuckbox = {'height': 30, 'width': 20, 'depth': 10}
        with open(os.path.dirname(__file__)+"/front.jpg", "rb") as front, open(os.path.dirname(__file__)+"/back.jpg", "rb") as back, open(os.path.dirname(__file__)+"/left.jpg", "rb") as left, open(os.path.dirname(__file__)+"/right.jpg", "rb") as right, open(os.path.dirname(__file__)+"/top.jpg", "rb") as top, open(os.path.dirname(__file__)+"/bottom.jpg", "rb") as bottom:
            faces = {'front': front, 'back': back, 'left': left,
                    'right': right, 'top': top, 'bottom': bottom}
            my_box = box.TuckBoxDrawing(tuckbox, paper, faces, None)

            if save_image:
                my_box.create_box_file(test_file)
                return

            i = my_box.draw_box()
            i.fuzz = i.quantum_range * 0.05
            ref_image = Image(filename=test_file)
            _, compare_metric = i.compare(ref_image, metric='absolute')

            self.assertLess(compare_metric, 1.0)

    def save_for_now(self):
        pass
        #with open(os.path.dirname(__file__)+"front.jpg", "rb") as front, open("house.png", "rb") as back, open("left.jpg", "rb") as left, open("right.jpg", "rb") as right, open("top.jpg", "rb") as top, open("bottom.jpg", "rb") as bottom:
        #    faces = {'front': front, 'back': back, 'left': left,
        #             'right': right, 'top': top, 'bottom': bottom}

if __name__ == "__main__":
    # Generate the test files
    test_class = BoxTestCase()
    object_methods = [method_name for method_name in dir(BoxTestCase)
                  if callable(getattr(BoxTestCase, method_name))]
    test_methods = list(filter(lambda s: s.startswith("test_"), object_methods))
    for method_name in test_methods:
        method_to_call = getattr(test_class, method_name)
        method_to_call(True)
    #test_class.test_AdjustLayout(True)
    #test_class.test_SimpleWhite(True)