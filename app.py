import gradio as gr
import http.server, json, uuid, queue, threading, os

tasks = {}
results = {}
waiters = queue.Queue()

# === HTTP 中继服务 ===
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/pull':
            self._json(200)
            try: tid = waiters.get(timeout=30); self.wfile.write(json.dumps(tasks.pop(tid, {"id":None})).encode())
            except: self.wfile.write(json.dumps({"id":None}).encode())
        elif self.path.startswith('/result/'):
            self._json(200)
            self.wfile.write(json.dumps(results.get(self.path.split('/')[-1], {"error":"not found"})).encode())
        else: self._json(404); self.wfile.write(b'{}')
    def do_POST(self):
        l = int(self.headers.get('Content-Length', 0))
        d = json.loads(self.rfile.read(l))
        if self.path == '/add':
            tid = str(uuid.uuid4())[:8]; tasks[tid] = {"id":tid, "command":d["command"]}; waiters.put(tid)
            self._json(200); self.wfile.write(json.dumps({"id":tid}).encode())
        elif self.path == '/push':
            results[d["id"]] = {"output":d.get("output",""), "exit_code":d.get("exit_code",0)}
            self._json(200); self.wfile.write(json.dumps({"ok":True}).encode())
        else: self._json(404); self.wfile.write(b'{}')
    def _json(self, code):
        self.send_response(code); self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*'); self.end_headers()
    def log_message(self, *a): pass

# === Gradio 界面 ===
def add_task(command):
    tid = str(uuid.uuid4())[:8]
    tasks[tid] = {"id": tid, "command": command}
    waiters.put(tid)
    return f"任务已发送: {tid}"

def check_result(task_id):
    r = results.get(task_id, None)
    return r["output"] if r else "等待中..."

with gr.Blocks(title="Relay Server") as demo:
    gr.Markdown("# 端云协同中继服务")
    with gr.Tab("发任务"):
        cmd = gr.Textbox(label="命令")
        btn = gr.Button("发送")
        out = gr.Textbox(label="结果")
        btn.click(add_task, inputs=[cmd], outputs=[out])
    with gr.Tab("查结果"):
        tid = gr.Textbox(label="任务ID")
        btn2 = gr.Button("查询")
        out2 = gr.Textbox(label="结果")
        btn2.click(check_result, inputs=[tid], outputs=[out2])

# 启动 HTTP 服务在后台
threading.Thread(target=lambda: http.server.HTTPServer(('0.0.0.0', 8765), H).serve_forever(), daemon=True).start()
demo.launch(server_name="0.0.0.0", server_port=7860)
