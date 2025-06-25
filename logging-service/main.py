from fastapi import FastAPI, Request
import hazelcast
import os
import uvicorn
import multiprocessing

def start_server(port,hazel_port):
    app = FastAPI()

    HZ_MEMBERS = os.environ.get("HZ_MEMBERS", f"127.0.0.1:{hazel_port}").split(",")
    hz = hazelcast.HazelcastClient(cluster_members=HZ_MEMBERS)
    map = hz.get_map("messages").blocking()

    @app.post("/log")
    async def log_message(req: Request):
        data = await req.json()
        msg_id = data.get("uuid")
        msg = data.get("msg")
        if msg_id and msg:
            map.put(msg_id, msg)
            print(f"[LoggingService:{port}] Logged: {msg_id} -> {msg}")
            return {"status": "ok"}
        return {"status": "error", "reason": "Missing fields"}

    @app.get("/log")
    async def get_all():
        entries = map.entry_set()
        return {"messages": [v for k, v in entries]}

    uvicorn.run(app, host="127.0.0.1", port=port, reload=False)

if __name__ == "__main__":
    # Запуск одночасно на портах 8001 і 8002
    p1 = multiprocessing.Process(target=start_server, args=(8001,5701))
    p2 = multiprocessing.Process(target=start_server, args=(8002,5702))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
