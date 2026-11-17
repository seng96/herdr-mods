# Git graph (WSL + Windows)

The Git graph panel from [rabeeh-ta/manygit](https://github.com/rabeeh-ta/manygit)
(MIT; cloned from Herdr's `git-graph` 0.1.15), with a `wsl-bridge.js` so it works when
Herdr runs on Windows, for repos inside WSL and in plain Windows folders.

## What changed from upstream

- New `wsl-bridge.js`; the modules import `exec` / `watchFolder` from it.
- **WSL folders:** `git`, `find`, `env` (and `openspec`) run inside the distro via
  `wsl.exe -d <distro> --cd <path> --exec ...`; output paths are mapped back to
  `//wsl$/<distro>/...`.
- **Windows folders:** Herdr's `exec` only starts `.exe` files and System32's
  `find.exe` is not GNU find, so `find` and `env` run Git for Windows' own
  (`C:/Program Files/Git/usr/bin/find.exe`, `env.exe`). `git` is `git.exe` on PATH.
- Remote machines (`on:`) are untouched.

`update.js` (upstream) only asks GitHub's releases API for a newer version and
opens the release page; it doesn't replace files.

## Status

The Windows-folder path passes `herdr-app check` but hasn't been confirmed in the
running app yet (it showed "Loading history…" when last looked at).

## Install

Copy `mods/git-graph-wsl/` to `~/.config/herdr-app/mods/` and point a layout block at
`{ "mod": "git-graph-wsl" }`. Needs Git for Windows at its default path.
