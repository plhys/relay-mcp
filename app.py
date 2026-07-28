import gradio as gr
import http.server, json, uuid, queue, threading, time

tasks = {}
results = {}
waiters = queue.Queue()

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

t = threading.Thread(target=http.server.HTTPServer(('0.0.0.0', 8765), H).serve_forever)
t.daemon = True
t.start()

demo = gr.Interface(fn=lambda x: "Relay Server Running", inputs="text", outputs="text", title="Relay")
demo.launch(server_name="0.0.0.0")
