# OpenSpec (WSL + Windows)

The OpenSpec side panel from [AshMcConnell/herdr-openspec](https://github.com/AshMcConnell/herdr-openspec)
(MIT; cloned from Herdr's `openspec` 0.1.15), made to work when Herdr runs on Windows,
for projects both inside WSL (`\\wsl$\<distro>\...`) and in plain Windows folders.

## What changed from upstream

Only `wsl-bridge.js` is new; `main.js` imports `exec`, `watchFolder` and
`normalizeFolder` from it instead of from `herdr`, and its shared-state keys and
self-references are renamed `openspec-wsl.*`.

- **WSL folders:** `git`, `find` and `openspec` run inside the distro through
  `wsl.exe -d <distro> --cd <path> --exec ...`, loading nvm first for `openspec`.
  Output paths are mapped back to `//wsl$/<distro>/...`. The Linux `openspec` is
  required; a Windows npm shim found on the WSL PATH is refused.
- **Windows folders:** Herdr's `exec` only starts `.exe` files, so
  - `openspec` (an npm `.cmd` shim) runs as `node <APPDATA>/npm/node_modules/@fission-ai/openspec/bin/openspec.js`;
  - `find` runs Git for Windows' GNU find, `C:/Program Files/Git/usr/bin/find.exe`
    (not System32's `find.exe`).
- Remote machines (`on:`) and every other command go to Herdr's `exec` unchanged.
- WSL folders aren't watched (`watchFolder` throws); the panel's poll timer covers them.

## Needs

- OpenSpec installed globally with npm (`npm i -g @fission-ai/openspec`) for Windows
  folders, and/or inside each WSL distro for WSL folders.
- Git for Windows at its default path.

## Install

Copy `mods/openspec-wsl/` to `~/.config/herdr-app/mods/` and point a layout block at
`{ "mod": "openspec-wsl" }` (e.g. a child of the right-hand panel stack).
`herdr-app check ~/.config/herdr-app/mods/openspec-wsl` should pass.

## Done when

- In a Windows project with `openspec/`, the panel lists its changes and task counts
  instead of "openspec is not installed".
- In a WSL project, the same, with paths shown as `//wsl$/...`.
