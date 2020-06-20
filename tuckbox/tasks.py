from celery import shared_task
from celery.result import AsyncResult
from . import box


@shared_task(bind=True)
def build_box(self, parameters):
    my_box = box.TuckBoxDrawing(parameters['tuckbox'],
                                parameters['paper'], parameters['faces'], parameters['options'])

    my_box.create_box_file(parameters['filename'])

    return "success"

def get_status(task_id):
    work = AsyncResult(task_id)
    if work and work.ready():
        result = work.get(timeout=1)
        return result.filename
    else:
        return None
