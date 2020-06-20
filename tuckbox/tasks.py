
import tempfile
from celery import shared_task
from django.conf import settings
from . import box


@shared_task(bind=True)
def build_box(self, parameters, task_id=None):
    my_box = box.TuckBoxDrawing(parameters['tuckbox'],
                                parameters['paper'], parameters['faces'], parameters['options'])

    result_pdf = tempfile.NamedTemporaryFile(delete=False, dir = settings.TMP_ROOT, suffix=".pdf")

    my_box.create_box_file(result_pdf.name)

    return str(self.request.id) + " -- " + result_pdf.name
