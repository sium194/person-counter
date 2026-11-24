import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class RuleBasedPersonCounter:
    def __init__(self, max_capacity: int = 5):
        self.max_capacity = max_capacity
        self.current_count = 0
        self.total_entered = 0
        self.total_exited = 0
        self.logs = []

    def _add_log(self, message: str):
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        self.logs.insert(0, f"[{timestamp}] {message}")
        self.logs = self.logs[:30]

    def get_status(self) -> str:
        if self.current_count == 0:
            return "Empty"
        elif self.current_count < self.max_capacity:
            return "Space Available"
        elif self.current_count == self.max_capacity:
            return "Capacity Reached"
        return "Warning: Over Capacity!"

    def entry(self):
        self.current_count += 1
        self.total_entered += 1
        self._add_log(f"Entry recorded (Current: {self.current_count})")
        return self.state()

    def exit(self):
        if self.current_count == 0:
            self._add_log("Exit ignored — already 0")
            return self.state()
        self.current_count -= 1
        self.total_exited += 1
        self._add_log(f"Exit recorded (Current: {self.current_count})")
        return self.state()

    def set_capacity(self, new_cap: int):
        self.max_capacity = max(1, new_cap)
        self._add_log(f"Max capacity set to {self.max_capacity}")
        return self.state()

    def reset(self):
        self.current_count = 0
        self.total_entered = 0
        self.total_exited = 0
        self.logs = []
        self._add_log("Counter reset")
        return self.state()

    def state(self) -> dict:
        return {
            "current_count": self.current_count,
            "max_capacity": self.max_capacity,
            "total_entered": self.total_entered,
            "total_exited": self.total_exited,
            "status": self.get_status(),
            "logs": self.logs,
        }


counter = RuleBasedPersonCounter(max_capacity=5)


class CounterHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code: int = 200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        if self.path == "/api/status":
            self._set_headers(200)
            self.wfile.write(json.dumps(counter.state()).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"

        if self.path == "/api/entry":
            data = counter.entry()
        elif self.path == "/api/exit":
            data = counter.exit()
        elif self.path == "/api/reset":
            data = counter.reset()
        elif self.path == "/api/capacity":
            payload = json.loads(body or "{}")
            new_cap = int(payload.get("max_capacity", 5))
            data = counter.set_capacity(new_cap)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))
            return

        self._set_headers(200)
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format, *args):
        return  # অপ্রয়োজনীয় কনসোল লগ কমিয়ে সার্ভার হালকা রাখবে


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), CounterHandler)
    print("Lightweight Counter Server running on http://0.0.0.0:8000")
    server.serve_forever()