import sys
import threading
from flask import Flask, render_template_string
import time

# Global buffer to store console output
log_buffer = []

class ConsoleCapture:
    def __init__(self, original):
        self.original = original

    def write(self, message):
        self.original.write(message)
        log_buffer.append(message)

    def flush(self):
        self.original.flush()

# Replace standard output and error with our custom streams.
sys.stdout = ConsoleCapture(sys.stdout)
sys.stderr = ConsoleCapture(sys.stderr)

app = Flask(__name__)

template = """
<!DOCTYPE html>
<html>
<head>
  <title>Program Console Output</title>
  <style>
    body { 
      font-family: monospace; 
      white-space: pre-wrap; 
      background-color: #000; 
      color: #0F0;
      margin: 0;
      padding: 1em;
    }
  </style>
</head>
<body>
  <h1>AI Smart Home Console Output</h1>
  <pre>{{ logs }}</pre>
  <script>
    // Auto-refresh every 3 seconds.
    setTimeout(function(){ window.location.reload(); }, 300000);
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    logs = "".join(log_buffer[-1000:])
    return render_template_string(template, logs=logs)

def run_web_server():
    # Listen on all available network interfaces so that any device on the same network can access the page.
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def start_web_console():
    thread = threading.Thread(target=run_web_server, daemon=True)
    thread.start()

if __name__ == "__main__":
    start_web_console()
    while True:
        print("Test message at", time.ctime())
        time.sleep(60)
