import time
import threading
import requests
import fastapi

received_list = []

app = fastapi.FastAPI()


@app.post("/api")
async def get_values(request: fastapi.Request):
    global received_list
    # Add the new entry to the back of the stack
    received_list.append(await request.json())
    return {"status": "success"}


def stack_extractor():
    global received_list
    # Extract the entry from back the stack and send it via a post
    while True:
        if len(received_list) > 0:
            last_entry = received_list.pop()
            requests.put("http://localhost:4000/api/", json=last_entry)
            time.sleep(1)
        else:
            time.sleep(1)


extractor_threads = 3
extractors = [threading.Thread(target=stack_extractor) for i in range(extractor_threads)]

for thread in extractors:
    thread.start()
