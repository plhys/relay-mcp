# relay-mcp

纯云卌同中绫 MCP Server，提供任务队列功能。

## 工具

- `send_task(command)` - 发送任务
- ` pull_task()` - 拉取任务
- `push_result(task_id, output)` - 回传结果
- `get_result(task_id)` - 查询结果