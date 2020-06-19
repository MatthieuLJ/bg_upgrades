
from celery import shared_task


@shared_task
def test(param):
    print("I'm running! with argument %s" % param)
    return 'The test task executed with argument "%s" ' % param
