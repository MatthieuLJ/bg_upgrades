import os
from celery import shared_task
from celery.result import AsyncResult
from django.conf import settings
from . import box


@shared_task(bind=True)
def build_box(self, parameters):
    my_box = box.TuckBoxDrawing(parameters['tuckbox'],
                                parameters['paper'], parameters['faces'], parameters['options'])

    my_box.create_box_file(parameters['filename'])

    # TODO: Should set a timeout timer here to forget the tasks / delete the file from here

    return os.path.basename(parameters['filename'])

def get_status(task_id):
    work = AsyncResult(task_id)
    if work.state == "SUCCESS":
        return "SUCCESS", work.get()
    else:
        return work.state, None