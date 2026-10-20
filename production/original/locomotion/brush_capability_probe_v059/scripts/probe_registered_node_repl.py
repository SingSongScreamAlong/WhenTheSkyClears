"""Read-only MCP discovery of the already registered node_repl server."""

import json
import os
import queue
import subprocess
import threading


def line_with_timeout(stream, seconds=10):
    result = queue.Queue(maxsize=1)
    thread = threading.Thread(target=lambda: result.put(stream.readline()), daemon=True)
    thread.start()
    try:
        return result.get(timeout=seconds)
    except queue.Empty:
        return None


config_call = subprocess.run(
    [r"WTSC_LOCAL_USER\AppData\Roaming\npm\codex.cmd", "mcp", "get", "node_repl", "--json"],
    capture_output=True, text=True, timeout=10, check=True,
)
transport = json.loads(config_call.stdout)["transport"]
env = dict(os.environ)
env.update(transport.get("env") or {})
process = subprocess.Popen(
    [transport["command"], *transport.get("args", [])],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, encoding="utf-8", bufsize=1, env=env,
    cwd=transport.get("cwd") or None,
)


def send(message):
    process.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
    process.stdin.flush()


try:
    send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"brush-capability-probe","version":"0.1"}}})
    first = line_with_timeout(process.stdout)
    if not first:
        print(json.dumps({"state":"initialize_timeout","returncode":process.poll()}))
    else:
        parsed = json.loads(first)
        print(json.dumps({"state":"initialize_response","result":parsed.get("result"),"error":parsed.get("error")}))
        if parsed.get("result"):
            send({"jsonrpc":"2.0","method":"notifications/initialized"})
            send({"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}})
            second = line_with_timeout(process.stdout)
            if second:
                listed = json.loads(second)
                print(json.dumps({"state":"tools_list","tools":[{"name":x.get("name"),"description":(x.get("description") or "")[:180],"inputSchema":x.get("inputSchema") if x.get("name")=="js" else None} for x in listed.get("result",{}).get("tools",[])],"error":listed.get("error")}))
            else:
                print(json.dumps({"state":"tools_list_timeout","returncode":process.poll()}))
finally:
    process.terminate()
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        process.kill()
