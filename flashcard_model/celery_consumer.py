from celery import Celery

app = Celery('flashcard_model')
app.conf.task_default_queue = "flashcard_model"
app.conf.task_default_routing_key = "flashcard_model.task"


@app.task(name="generate_flashcard")
def generate_flashcard(content):
    print("Task received")
