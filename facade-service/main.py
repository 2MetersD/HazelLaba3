from fastapi import FastAPI, Request
import requests
import random
import uuid
import os
import uvicorn

app = FastAPI()

LOGGING_SERVICES = os.environ.get("LOGGING_SERVICES", "http://localhost:8001,http://localhost:8002").split(",")
MESSAGES_SERVICE = os.environ.get("MESSAGES_SERVICE", "http://localhost:8010")

@app.post("/")
async def post_msg(req: Request):
    data = await req.json()
    msg = data.get("msg")
    if not msg:
        return {"error": "msg field required"}

    msg_id = str(uuid.uuid4())
    payload = {"uuid": msg_id, "msg": msg}
    random.shuffle(LOGGING_SERVICES)

    for url in LOGGING_SERVICES:
        try:
            r = requests.post(f"{url}/log", json=payload, timeout=2)
            if r.status_code == 200:
                return {"status": "ok", "uuid": msg_id}
        except:
            continue

    return {"status": "error", "reason": "all logging-services failed"}

@app.get("/")
async def get_combined():
    logs = []
    msgs = []

    for url in random.sample(LOGGING_SERVICES, len(LOGGING_SERVICES)):
        try:
            r = requests.get(f"{url}/log", timeout=2)
            if r.status_code == 200:
                logs = r.json().get("messages", [])
                break
        except:
            continue

    try:
        r = requests.get(f"{MESSAGES_SERVICE}/msg")
        if r.status_code == 200:
            msgs = r.text
    except:
        msgs = "messages-service unavailable"

    return {"logs": logs, "messages-service": msgs}

if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
