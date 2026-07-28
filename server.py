import json, uuid
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationCapabilities
from mcp.server.stdio import stdio_server
from datetime import datetime

tasks = {}

server = Server("relay")

@server.tool()
async def send_task(command: str) -> str:
    tid = str(uuid.uuid4())[:8]
    tasks[tid] = {"command": command, "status": "pending", "result": None, "time": str(datetime.now())}
    return json.dumps({"task_id": tid, "status": "pending"})

@server.tool()
async def get_result(task_id: str) -> str:
    t = tasks.get(task_id)
    return json.dumps(t) if t else json.dumps({"error": "not found"})

@server.tool()
async def pull_task() -> str:
    for tid, t in tasks.items():
        if t["status"] == "pending":
            t["status"] = "running"
            return json.dumps({"task_id": tid, "command": t["command"]})
    return json.dumps({"task_id": None})

@server.tool()
async def push_result(task_id: str, output: str) -> str:
    if task_id in tasks:
        tasks[task_id]["status"] = "done"
        tasks[task_id]["result"] = output
        return json.dumps({"ok": True})
    return json.dumps({"error": "not found"})

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())
