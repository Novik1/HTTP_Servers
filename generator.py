import random
import string
import time
import threading
import requests
import fastapi
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

initial_list = []
processed_list = []
app = fastapi.FastAPI()

templates = Jinja2Templates(directory="templates")

# Entrypoint for display
@app.get("/")
def display():
    global initial_list
    global processed_list
    context = {"request": {"initial": str(initial_list), "processed": str(processed_list)}}
    return templates.TemplateResponse("index.html", context)


# Entrypoint for return string values
@app.put("/api")
async def get_back(request: fastapi.Request):
    global processed_list
    processed_list.insert(0, await request.json())
    if processed_list.__len__() > 10:
        processed_list.pop()
    return {"status": "success"}


@app.get("/stop")
def stop():
    global run_condition
    run_condition = False
    return RedirectResponse(url='/')


@app.get("/run")
def run():
    global run_condition
    run_condition = True
    return RedirectResponse(url='/')


def generator_func():
    global initial_list
    while True:
        while run_condition:
            initial_list.insert(0, get_random_string())
            time.sleep(1)
        time.sleep(3)


def get_random_string():
    # choose from all lowercase letter
    length = 8
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def queue_extractor():
    global initial_list
    # Extract the last entry from the queue and send it via a post
    while True:
        if len(initial_list) > 0:
            last_entry = initial_list.pop()
            requests.post("http://localhost:4001/api/", json=last_entry)
            time.sleep(1)
        else:
            time.sleep(1)


extractor_threads = 2
generator_threads = 8
run_condition = False
extractors = [threading.Thread(target=queue_extractor) for i in range(extractor_threads)]
generators = [threading.Thread(target=generator_func) for i in range(generator_threads)]

for thread in extractors:
    thread.start()
for thread in generators:
    thread.start()
