from celery import shared_task


@shared_task
def print_hello():
    logger = print_hello.get_logger()
    logger.info("Hello")
