import json, uuid
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio

tasks = {}

async def send_task(command: str) -> str:
    tid = str(uuid.uuid4())[:8]
    tasks[tid] = {"command": command, "status": "pending", "result": None, "time": str(datetime.now())}
    return json.dumps({"task_id": tid, "status": "pending"})

async def get_result(task_id: str) -> str:
    t = tasks.get(task_id)
    return json.dumps(t) if t else json.dumps({"error": "not found"})

async def pull_task() -> str:
    for tid, t in tasks.items():
        if t["status"] == "pending":
            t["status"] = "running"
            return json.dumps({"task_id": tid, "command": t["command"]})
    return json.dumps({"task_id": None})

async def push_result(task_id: str, output: str) -> str:
    if task_id in tasks:
        tasks[task_id]["status"] = "done"
        tasks[task_id]["result"] = output
        return json.dumps({"ok": True})
    return json.dumps({"error": "not found"})

async def main():
    server = Server("relay")
    
    @server.tool()
    async def send_task_tool(command: str) -> str:
        return await send_task(command)
    
    @server.tool()
    async def get_result_tool(task_id: str) -> str:
        return await get_result(task_id)
    
    @server.tool()
    async def pull_task_tool() -> str:
        return await pull_task()
    
    @server.tool()
    async def push_result_tool(task_id: str, output: str) -> str:
        return await push_result(task_id, output)
    
    async with stdio_server() as (read, write):
        await server.run(read, write)

if __name__ == "__main__":
    asyncio.run(main())
