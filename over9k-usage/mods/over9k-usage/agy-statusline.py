#!/usr/bin/env python3
# Local fit (Windows, no sh/jq) of Over9k's agy-statusline.sh, usage part only:
# Antigravity CLI hands its status line the quota buckets (gemini-5h, gemini-weekly,
# 3p-5h, 3p-weekly) and plan; they are saved to ~/.cache/over9k/usage/antigravity.json
# for over9k-usage's Gemini row, and a short limits line is printed under agy's own
# (stack_with_default). No network; writes only that one file.
import json, os, sys, time

try:
    d = json.loads(sys.stdin.buffer.read().decode("utf-8", errors="replace"))
except ValueError:
    sys.exit(0)
q = d.get("quota")
now = int(time.time())

if q:
    u = os.path.join(os.path.expanduser("~"), ".cache", "over9k", "usage")
    path = os.path.join(u, "antigravity.json")
    try:
        with open(path, encoding="utf-8") as f:
            saved = (json.load(f) or {}).get("quota") or {}
    except (OSError, ValueError):
        saved = {}

    # Every running agy writes here, some with older numbers: per bucket keep the later
    # reset, and for the same reset the most used.
    def newest(new, old):
        if not old:
            return new
        nr, orr = new.get("reset_time") or "", old.get("reset_time") or ""
        if nr > orr:
            return new
        if nr < orr:
            # The old bucket's reset_in_seconds was relative to when it was saved.
            try:
                import datetime
                t = datetime.datetime.fromisoformat(orr.replace("Z", "+00:00")).timestamp()
                return dict(old, reset_in_seconds=max(0, int(t - now)))
            except ValueError:
                return old
        if (old.get("remaining_fraction", 1) or 0) < (new.get("remaining_fraction", 1) or 0):
            return dict(new, remaining_fraction=old.get("remaining_fraction"))
        return new

    merged = {k: newest(v, saved.get(k)) for k, v in q.items() if isinstance(v, dict)}
    try:
        os.makedirs(u, exist_ok=True)
        tmp = "%s.%d" % (path, os.getpid())
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"at": now, "plan": d.get("plan_tier"), "quota": merged}, f)
        try:
            os.replace(tmp, path)
        except OSError:
            os.remove(tmp)  # target busy (Windows): the next refresh writes it
    except OSError:
        pass


def left(s):
    s = int(s or 0)
    if s <= 0:
        return "now"
    if s < 3600:
        return "%dm" % (s // 60)
    if s < 86400:
        return "%dh %dm" % (s // 3600, s % 3600 // 60)
    return "%dd %dh" % (s // 86400, s % 86400 // 3600)


def pct(used):
    c = "31" if used >= 80 else "33" if used >= 50 else "32"
    return "\x1b[%sm%d%%\x1b[0m" % (c, round(used))


def bucket(key, label):
    b = (q or {}).get(key)
    if not isinstance(b, dict):
        return None
    used = (1 - (b.get("remaining_fraction") if b.get("remaining_fraction") is not None else 1)) * 100
    return "%s %s \x1b[2m· %s\x1b[0m" % (label, pct(used), left(b.get("reset_in_seconds")))


gem = str((d.get("model") or {}).get("display_name") or "").lower().startswith("gemini")
mine, other, other_name = ("gemini", "3p", "Claude/GPT") if gem else ("3p", "gemini", "Gemini")
parts = []
ctx = (d.get("context_window") or {}).get("used_percentage")
if ctx is not None:
    parts.append("context " + pct(ctx))
parts += [x for x in (bucket(mine + "-5h", "5h"), bucket(mine + "-weekly", "week")) if x]
others = [x for x in (bucket(other + "-5h", "5h"), bucket(other + "-weekly", "week")) if x]
if others:
    parts.append(other_name + " " + "   ".join(others))
sys.stdout.buffer.write("   ".join(parts).encode("utf-8"))
