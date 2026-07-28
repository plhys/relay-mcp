import sys, json, uuid

tasks = {}

def main():
    print("MCP Server ready", file=sys.stderr, flush=True)
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            req = json.loads(line)
            method = req.get("method", "")
            req_id = req.get("id")
            
            if method == "initialize":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "relay", "version": "0.1.0"}
                }}
            elif method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": [
                    {"name": "send_task", "description": "send a task", "inputSchema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
                    {"name": "pull_task", "description": "pull a pending task", "inputSchema": {"type": "object", "properties": {}}},
                    {"name": "push_result", "description": "push task result", "inputSchema": {"type": "object", "properties": {"task_id": {"type": "string"}, "output": {"type": "string"}}, "required": ["task_id", "output"]}},
                    {"name": "get_result", "description": "get task result", "inputSchema": {"type": "object", "properties": {"task_id": {"type": "string"}}, "required": ["task_id"]}}
                ]}}
            elif method == "tools/call":
                tool_name = req["params"]["name"]
                args = req["params"].get("arguments", {})
                if tool_name == "send_task":
                    tid = str(uuid.uuid4())[:8]
                    tasks[tid] = {"command": args["command"], "status": "pending", "result": None}
                    result = json.dumps({"task_id": tid, "status": "pending"})
                elif tool_name == "pull_task":
                    for tid, t in tasks.items():
                        if t["status"] == "pending":
                            t["status"] = "running"
                            result = json.dumps({"task_id": tid, "command": t["command"]})
                            break
                    else:
                        result = json.dumps({"task_id": None})
                elif tool_name == "push_result":
                    if args["task_id"] in tasks:
                        tasks[args["task_id"]]["status"] = "done"
                        tasks[args["task_id"]]["result"] = args["output"]
                        result = json.dumps({"ok": True})
                    else:
                        result = json.dumps({"error": "not found"})
                elif tool_name == "get_result":
                    t = tasks.get(args["task_id"])
                    result = json.dumps(t) if t else json.dumps({"error": "not found"})
                else:
                    result = json.dumps({"error": "unknown tool"})
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": result}]}}
            elif method == "notifications/initialized":
                continue
            else:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
            
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    main()
