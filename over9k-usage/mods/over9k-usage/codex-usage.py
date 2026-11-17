#!/usr/bin/env python3
# Local fit (Windows without sh/jq): Codex's latest rate_limits, as the upstream
# CODEX shell line printed it: {"plan", "primary", "secondary"} or nothing.
# Reads only ~/.codex/sessions; writes nothing.
import glob, json, os, sys

root = os.path.join(os.path.expanduser("~"), ".codex", "sessions")
files = glob.glob(os.path.join(root, "*", "*", "*", "*.jsonl"))
if not files:
    sys.exit(0)
newest = max(files, key=lambda p: os.path.getmtime(p))
with open(newest, "rb") as f:
    f.seek(0, os.SEEK_END)
    size = f.tell()
    chunk = 1 << 20
    data = b""
    # Read backwards until a rate_limits object shows up (or the whole file is read).
    while True:
        start = max(0, size - chunk)
        f.seek(start)
        data = f.read(size - start).decode("utf-8", errors="replace")
        if '"rate_limits":{' in data or start == 0:
            break
        chunk *= 4
at = data.rfind('"rate_limits":{')
if at < 0:
    sys.exit(0)
try:
    rl, _ = json.JSONDecoder().raw_decode(data, at + len('"rate_limits":'))
except ValueError:
    sys.exit(0)
print(json.dumps({"plan": rl.get("plan_type"), "primary": rl.get("primary"), "secondary": rl.get("secondary")}))
