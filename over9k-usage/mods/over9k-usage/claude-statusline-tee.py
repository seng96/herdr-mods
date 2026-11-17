#!/usr/bin/env python3
# Local fit (Windows, no sh/jq): Claude Code's status line input passes through to the
# person's own status line unchanged (ccstatusline), and its rate_limits are saved to
# ~/.cache/over9k/usage/claude.json for over9k-usage's Claude row. No network; writes
# only that one file.
#   statusLine.command: python -I "<this file>" bunx -y ccstatusline@latest
import json, os, subprocess, sys, time

data = sys.stdin.buffer.read()
try:
    d = json.loads(data.decode("utf-8", errors="replace"))
    rl = d.get("rate_limits")
    if rl:
        u = os.path.join(os.path.expanduser("~"), ".cache", "over9k", "usage")
        os.makedirs(u, exist_ok=True)
        tmp = os.path.join(u, "claude.json.%d" % os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"at": int(time.time()), "five_hour": rl.get("five_hour"), "seven_day": rl.get("seven_day")}, f)
        try:
            os.replace(tmp, os.path.join(u, "claude.json"))
        except OSError:
            os.remove(tmp)  # target busy (Windows): the next refresh writes it
except Exception:
    pass
cmd = sys.argv[1:]
if cmd:
    r = subprocess.run(subprocess.list2cmdline(cmd), input=data, stdout=subprocess.PIPE, shell=True)
    sys.stdout.buffer.write(r.stdout)
    sys.exit(r.returncode)
