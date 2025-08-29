from celery import Celery

celery = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery.task
def simulate_job():
    """
    This function simulates a worker job by printing a message.
    """
    print("Simulating a worker job...")