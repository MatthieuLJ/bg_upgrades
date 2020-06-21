import os
from celery import shared_task
from celery.result import AsyncResult
from django.conf import settings
from . import box


@shared_task(bind=True)
def build_box(self, parameters):
    faces_files = {}
    for face in parameters['faces']:
        faces_files[face] = open(parameters['faces'][face], 'rb')
    my_box = box.TuckBoxDrawing(parameters['tuckbox'],
                                parameters['paper'], faces_files, parameters['options'])

    def progress_tracker(percent):
        print("Getting progress "+str(percent))
        self.update_state(
            state="STARTED" if percent<100 else "SAVING",
            meta={
                'percent': percent,
            }
        )

    my_box.create_box_file(parameters['filename'], progress_tracker)

    for face in parameters['faces']:
        faces_files[face].close()
        os.remove(parameters['faces'][face])
    # TODO: Should set a timeout timer here to forget the tasks / delete the file from here

    return settings.TMP_URL + os.path.basename(parameters['filename'])


def get_status(task_id):
    work = AsyncResult(task_id)
    if work.state == "SUCCESS":
        return "SUCCESS", work.get()
    else:
        return work.state, work.info
